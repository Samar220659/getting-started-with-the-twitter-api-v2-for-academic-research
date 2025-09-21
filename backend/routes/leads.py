from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
import uuid
from datetime import datetime

from models.leads import SearchRequest, LeadResult, SearchRecord, EmailEnrichmentRequest, DashboardStats
from services.lead_scraper import MockLeadScraperService, MockEmailEnrichmentService
from server import db

router = APIRouter(prefix="/api/leads", tags=["leads"])

# Initialize services
scraper_service = MockLeadScraperService()
email_service = MockEmailEnrichmentService()

@router.post("/scrape", response_model=dict)
async def scrape_google_maps(search_request: SearchRequest, background_tasks: BackgroundTasks):
    """
    Scrape Google Maps for local business leads
    """
    try:
        # Create search record
        search_record = SearchRecord(
            query=search_request.query,
            city=search_request.city,
            state=search_request.state,
            zipCode=search_request.zipCode,
            maxResults=search_request.maxResults
        )
        
        # Save search record to database
        search_dict = search_record.dict()
        await db.searches.insert_one(search_dict)
        search_id = search_dict["id"]
        
        # Scrape leads (this includes the realistic delay)
        leads = await scraper_service.scrape_google_maps(search_request, search_id)
        
        # Save leads to database
        leads_data = []
        for lead in leads:
            lead_dict = lead.dict()
            leads_data.append(lead_dict)
            
        if leads_data:
            await db.leads.insert_many(leads_data)
            
        # Update search record with results count
        await db.searches.update_one(
            {"id": search_id},
            {"$set": {"results_count": len(leads_data)}}
        )
        
        return {
            "searchId": search_id,
            "results": leads_data,
            "count": len(leads_data),
            "message": f"Successfully scraped {len(leads_data)} leads for '{search_request.query}' in {search_request.city}, {search_request.state}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@router.post("/enrich-email", response_model=dict)
async def enrich_email(request: EmailEnrichmentRequest):
    """
    Enrich lead with email address using Hunter.io-style service
    """
    try:
        # Get the lead from database
        lead = await db.leads.find_one({"id": request.leadId})
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        if not request.website:
            raise HTTPException(status_code=400, detail="Website URL is required for email enrichment")
        
        # Attempt to enrich email
        enriched_email = await email_service.enrich_email(request.website)
        
        if enriched_email:
            # Update lead with enriched email
            await db.leads.update_one(
                {"id": request.leadId},
                {"$set": {"email": enriched_email}}
            )
            
            # Log enrichment activity
            enrichment_record = {
                "id": str(uuid.uuid4()),
                "leadId": request.leadId,
                "website": request.website,
                "enrichedEmail": enriched_email,
                "source": "hunter_mock",
                "created_at": datetime.utcnow()
            }
            await db.email_enrichments.insert_one(enrichment_record)
            
            return {
                "success": True,
                "email": enriched_email,
                "message": "Email successfully enriched"
            }
        else:
            return {
                "success": False,
                "email": None,
                "message": "No email found for this website"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email enrichment failed: {str(e)}")

@router.get("/search/{search_id}", response_model=dict)
async def get_search_results(search_id: str):
    """
    Get results for a specific search
    """
    try:
        # Get search record
        search = await db.searches.find_one({"id": search_id})
        if not search:
            raise HTTPException(status_code=404, detail="Search not found")
        
        # Get associated leads
        leads_cursor = db.leads.find({"searchId": search_id})
        leads = await leads_cursor.to_list(1000)
        
        return {
            "search": search,
            "leads": leads,
            "count": len(leads)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve search results: {str(e)}")

@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """
    Get dashboard statistics and metrics
    """
    try:
        # Get total counts
        total_leads = await db.leads.count_documents({})
        total_searches = await db.searches.count_documents({})
        enriched_emails = await db.email_enrichments.count_documents({})
        
        # Calculate conversion rate (leads with emails / total leads)
        leads_with_emails = await db.leads.count_documents({"email": {"$ne": None, "$ne": ""}})
        avg_conversion = (leads_with_emails / total_leads * 100) if total_leads > 0 else 0
        
        # Get recent searches
        recent_searches_cursor = db.searches.find().sort("created_at", -1).limit(5)
        recent_searches = await recent_searches_cursor.to_list(5)
        
        # Format recent searches for frontend
        formatted_searches = []
        for search in recent_searches:
            formatted_searches.append({
                "id": search["id"],
                "query": f"{search['query']} in {search['city']}, {search['state']}",
                "results": search.get("results_count", 0),
                "date": search["created_at"].strftime("%Y-%m-%d %H:%M"),
                "avgRating": 4.3  # Mock average rating
            })
        
        return DashboardStats(
            totalLeads=total_leads,
            totalSearches=total_searches,
            avgConversion=round(avg_conversion, 1),
            emailsEnriched=enriched_emails,
            recentSearches=formatted_searches
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve dashboard stats: {str(e)}")

@router.get("/export/{search_id}")
async def export_search_results(search_id: str):
    """
    Export search results as CSV
    """
    try:
        # Get search and leads
        search = await db.searches.find_one({"id": search_id})
        if not search:
            raise HTTPException(status_code=404, detail="Search not found")
            
        leads_cursor = db.leads.find({"searchId": search_id})
        leads = await leads_cursor.to_list(1000)
        
        if not leads:
            raise HTTPException(status_code=404, detail="No leads found for this search")
        
        # Generate CSV content
        headers = ["Business Name", "Type", "Address", "Phone", "Website", "Email", "Rating", "Reviews", "Search Query"]
        
        csv_lines = [",".join(f'"{header}"' for header in headers)]
        
        for lead in leads:
            row = [
                lead.get("businessName", ""),
                lead.get("businessType", ""),
                lead.get("address", ""),
                lead.get("phone", ""),
                lead.get("website", ""),
                lead.get("email", ""),
                str(lead.get("rating", "")),
                str(lead.get("reviewCount", "")),
                search["query"]
            ]
            csv_lines.append(",".join(f'"{field}"' for field in row))
        
        csv_content = "\n".join(csv_lines)
        
        return {
            "csv_content": csv_content,
            "filename": f"leads_{search['query'].replace(' ', '_')}_{search['city']}_{datetime.now().strftime('%Y%m%d')}.csv",
            "count": len(leads)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")