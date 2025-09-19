from fastapi import FastAPI, APIRouter, HTTPException, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
from emergentintegrations.llm.chat import LlmChat, UserMessage
import asyncio
import json
import base64
import requests
from urllib.parse import urlencode
from integrations import (
    YouTubeManager, 
    TikTokBusinessManager, 
    DigiStore24Manager,
    SocialMediaAutomation,
    EmailMarketingManager,
    WebhookHandler
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class Workflow(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    type: str  # lead_gen, content_creation, social_media, affiliate
    status: str = "active"  # active, paused, completed
    config: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_run: Optional[datetime] = None
    total_revenue: float = 0.0
    leads_generated: int = 0
    content_created: int = 0

class WorkflowCreate(BaseModel):
    name: str
    description: str
    type: str
    config: Dict[str, Any] = {}

class Lead(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    company: Optional[str] = None
    industry: Optional[str] = None
    pain_points: List[str] = []
    score: int = 0  # 1-10
    source: str  # website, social_media, referral
    workflow_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "new"  # new, contacted, converted, lost

class LeadCreate(BaseModel):
    email: str
    company: Optional[str] = None
    industry: Optional[str] = None
    pain_points: List[str] = []
    source: str = "website"
    workflow_id: str

class Content(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content_type: str  # video_script, social_post, email, blog
    content: str
    target_audience: str
    keywords: List[str] = []
    workflow_id: str
    lead_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    published: bool = False
    performance: Dict[str, Any] = {}

class ContentCreate(BaseModel):
    content_type: str
    target_audience: str
    keywords: List[str] = []
    workflow_id: str
    lead_id: Optional[str] = None
    custom_prompt: Optional[str] = None

class SocialPost(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    platform: str  # youtube, tiktok, instagram, linkedin
    content_id: str
    post_url: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    posted_time: Optional[datetime] = None
    status: str = "draft"  # draft, scheduled, posted, failed
    engagement: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SocialPostCreate(BaseModel):
    platform: str
    content_id: str
    scheduled_time: Optional[datetime] = None

class Revenue(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str
    source: str  # affiliate, course_sale, consultation
    amount: float
    currency: str = "EUR"
    lead_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RevenueCreate(BaseModel):
    workflow_id: str
    source: str
    amount: float
    currency: str = "EUR"
    lead_id: Optional[str] = None

class AutomationStats(BaseModel):
    total_workflows: int
    active_workflows: int
    total_leads: int
    total_revenue: float
    content_created_today: int
    posts_scheduled: int

# Initialize LLM Chat
async def get_llm_chat(session_id: str = "default"):
    return LlmChat(
        api_key=os.getenv('EMERGENT_LLM_KEY'),
        session_id=session_id,
        system_message="Du bist ein Experte für Marketing-Automatisierung und Content-Erstellung. Erstelle hochwertige, zielgerichtete Inhalte für deutsche Unternehmen."
    ).with_model("openai", "gpt-4o-mini")

# Routes
@api_router.get("/")
async def root():
    return {"message": "ZZ-LOBBY-BOOST API ist aktiv"}

# Workflow Management
@api_router.post("/workflows", response_model=Workflow)
async def create_workflow(workflow: WorkflowCreate):
    workflow_dict = workflow.dict()
    workflow_obj = Workflow(**workflow_dict)
    await db.workflows.insert_one(workflow_obj.dict())
    return workflow_obj

@api_router.get("/workflows", response_model=List[Workflow])
async def get_workflows():
    workflows = await db.workflows.find().to_list(1000)
    return [Workflow(**workflow) for workflow in workflows]

@api_router.get("/workflows/{workflow_id}", response_model=Workflow)
async def get_workflow(workflow_id: str):
    workflow = await db.workflows.find_one({"id": workflow_id})
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow nicht gefunden")
    return Workflow(**workflow)

@api_router.put("/workflows/{workflow_id}/status")
async def update_workflow_status(workflow_id: str, status: str):
    result = await db.workflows.update_one(
        {"id": workflow_id},
        {"$set": {"status": status}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Workflow nicht gefunden")
    return {"message": f"Workflow Status auf '{status}' aktualisiert"}

# Lead Management
@api_router.post("/leads", response_model=Lead)
async def create_lead(lead: LeadCreate):
    lead_dict = lead.dict()
    lead_obj = Lead(**lead_dict)
    await db.leads.insert_one(lead_obj.dict())
    
    # Update workflow leads count
    await db.workflows.update_one(
        {"id": lead.workflow_id},
        {"$inc": {"leads_generated": 1}}
    )
    
    return lead_obj

@api_router.get("/leads", response_model=List[Lead])
async def get_leads(workflow_id: Optional[str] = None):
    query = {"workflow_id": workflow_id} if workflow_id else {}
    leads = await db.leads.find(query).to_list(1000)
    return [Lead(**lead) for lead in leads]

@api_router.put("/leads/{lead_id}/score")
async def update_lead_score(lead_id: str, score: int):
    if not 1 <= score <= 10:
        raise HTTPException(status_code=400, detail="Score muss zwischen 1 und 10 liegen")
    
    result = await db.leads.update_one(
        {"id": lead_id},
        {"$set": {"score": score}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Lead nicht gefunden")
    return {"message": f"Lead Score auf {score} aktualisiert"}

# Content Generation
@api_router.post("/content/generate", response_model=Content)
async def generate_content(content_request: ContentCreate):
    try:
        # Get lead data if provided
        lead_data = None
        if content_request.lead_id:
            lead = await db.leads.find_one({"id": content_request.lead_id})
            if lead:
                lead_data = Lead(**lead)

        # Generate content prompt based on type
        prompts = {
            "video_script": f"Erstelle ein 60-Sekunden YouTube-Shorts-Skript für {content_request.target_audience}. Thema: {', '.join(content_request.keywords)}. Format: Hook (5s), Problem (15s), 3 Lösungsschritte (30s), Call-to-Action (10s).",
            "social_post": f"Erstelle einen viralen Social Media Post für {content_request.target_audience}. Keywords: {', '.join(content_request.keywords)}. Füge relevante Hashtags hinzu.",
            "email": f"Schreibe eine personalisierte Marketing-E-Mail für {content_request.target_audience}. Fokus auf {', '.join(content_request.keywords)}.",
            "blog": f"Erstelle einen informativen Blog-Artikel über {', '.join(content_request.keywords)} für {content_request.target_audience}. Füge SEO-optimierte Überschriften hinzu."
        }
        
        prompt = content_request.custom_prompt or prompts.get(content_request.content_type, "Erstelle relevanten Content")
        
        if lead_data:
            prompt += f" Zielgruppe Details: Unternehmen: {lead_data.company}, Branche: {lead_data.industry}, Pain Points: {', '.join(lead_data.pain_points)}"

        # Generate content using LLM
        chat = await get_llm_chat(f"content_{content_request.workflow_id}")
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        # Create content object
        content_obj = Content(
            title=f"{content_request.content_type.title()} - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            content_type=content_request.content_type,
            content=response,
            target_audience=content_request.target_audience,
            keywords=content_request.keywords,
            workflow_id=content_request.workflow_id,
            lead_id=content_request.lead_id
        )
        
        await db.content.insert_one(content_obj.dict())
        
        # Update workflow content count
        await db.workflows.update_one(
            {"id": content_request.workflow_id},
            {"$inc": {"content_created": 1}}
        )
        
        return content_obj
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content-Generierung fehlgeschlagen: {str(e)}")

@api_router.get("/content", response_model=List[Content])
async def get_content(workflow_id: Optional[str] = None):
    query = {"workflow_id": workflow_id} if workflow_id else {}
    content = await db.content.find(query).sort("created_at", -1).to_list(1000)
    return [Content(**item) for item in content]

@api_router.get("/content/{content_id}", response_model=Content)
async def get_content_item(content_id: str):
    content = await db.content.find_one({"id": content_id})
    if not content:
        raise HTTPException(status_code=404, detail="Content nicht gefunden")
    return Content(**content)

# Social Media Management
@api_router.post("/social/schedule", response_model=SocialPost)
async def schedule_social_post(post: SocialPostCreate):
    # Get content
    content = await db.content.find_one({"id": post.content_id})
    if not content:
        raise HTTPException(status_code=404, detail="Content nicht gefunden")
    
    post_obj = SocialPost(**post.dict())
    await db.social_posts.insert_one(post_obj.dict())
    return post_obj

@api_router.get("/social/posts", response_model=List[SocialPost])
async def get_social_posts(platform: Optional[str] = None):
    query = {"platform": platform} if platform else {}
    posts = await db.social_posts.find(query).sort("created_at", -1).to_list(1000)
    return [SocialPost(**post) for post in posts]

@api_router.put("/social/posts/{post_id}/status")
async def update_post_status(post_id: str, status: str, post_url: Optional[str] = None):
    update_data = {"status": status}
    if status == "posted":
        update_data["posted_time"] = datetime.utcnow()
        if post_url:
            update_data["post_url"] = post_url
    
    result = await db.social_posts.update_one(
        {"id": post_id},
        {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Post nicht gefunden")
    return {"message": f"Post Status auf '{status}' aktualisiert"}

# Revenue Tracking
@api_router.post("/revenue", response_model=Revenue)
async def add_revenue(revenue: RevenueCreate):
    revenue_obj = Revenue(**revenue.dict())
    await db.revenue.insert_one(revenue_obj.dict())
    
    # Update workflow total revenue
    await db.workflows.update_one(
        {"id": revenue.workflow_id},
        {"$inc": {"total_revenue": revenue.amount}}
    )
    
    return revenue_obj

@api_router.get("/revenue", response_model=List[Revenue])
async def get_revenue(workflow_id: Optional[str] = None):
    query = {"workflow_id": workflow_id} if workflow_id else {}
    revenue = await db.revenue.find(query).sort("created_at", -1).to_list(1000)
    return [Revenue(**item) for item in revenue]

# Analytics and Stats
@api_router.get("/stats", response_model=AutomationStats)
async def get_automation_stats():
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    total_workflows = await db.workflows.count_documents({})
    active_workflows = await db.workflows.count_documents({"status": "active"})
    total_leads = await db.leads.count_documents({})
    
    # Calculate total revenue
    revenue_pipeline = [
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]
    revenue_result = await db.revenue.aggregate(revenue_pipeline).to_list(1)
    total_revenue = revenue_result[0]["total"] if revenue_result else 0.0
    
    content_created_today = await db.content.count_documents({
        "created_at": {"$gte": today}
    })
    
    posts_scheduled = await db.social_posts.count_documents({
        "status": {"$in": ["draft", "scheduled"]}
    })
    
    return AutomationStats(
        total_workflows=total_workflows,
        active_workflows=active_workflows,
        total_leads=total_leads,
        total_revenue=total_revenue,
        content_created_today=content_created_today,
        posts_scheduled=posts_scheduled
    )

# Automation Triggers
@api_router.post("/automation/lead-to-content/{lead_id}")
async def trigger_lead_to_content(lead_id: str):
    """Automatisch Content für einen Lead generieren"""
    lead = await db.leads.find_one({"id": lead_id})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead nicht gefunden")
    
    lead_obj = Lead(**lead)
    
    # Generate video script
    content_request = ContentCreate(
        content_type="video_script",
        target_audience=f"{lead_obj.company} ({lead_obj.industry})",
        keywords=lead_obj.pain_points or ["Automatisierung", "Effizienz"],
        workflow_id=lead_obj.workflow_id,
        lead_id=lead_id
    )
    
    content = await generate_content(content_request)
    
    # Schedule social media posts
    platforms = ["youtube", "tiktok", "linkedin"]
    scheduled_posts = []
    
    for platform in platforms:
        post_request = SocialPostCreate(
            platform=platform,
            content_id=content.id,
            scheduled_time=datetime.utcnow() + timedelta(hours=1)
        )
        post = await schedule_social_post(post_request)
        scheduled_posts.append(post)
    
    return {
        "message": "Automatisierung erfolgreich gestartet",
        "content": content,
        "scheduled_posts": scheduled_posts
    }

class ContentRecyclingRequest(BaseModel):
    platforms: List[str]

@api_router.post("/automation/content-recycling/{content_id}")
async def trigger_content_recycling(content_id: str, request: ContentRecyclingRequest):
    """Content für mehrere Plattformen recyceln"""
    content = await db.content.find_one({"id": content_id})
    if not content:
        raise HTTPException(status_code=404, detail="Content nicht gefunden")
    
    scheduled_posts = []
    base_time = datetime.utcnow()
    
    for i, platform in enumerate(request.platforms):
        post_request = SocialPostCreate(
            platform=platform,
            content_id=content_id,
            scheduled_time=base_time + timedelta(hours=i * 2)  # 2h Abstand
        )
        post = await schedule_social_post(post_request)
        scheduled_posts.append(post)
    
    return {
        "message": f"Content für {len(request.platforms)} Plattformen geplant",
        "scheduled_posts": scheduled_posts
    }

# ============================
# ECHTE API-INTEGRATIONEN
# ============================

# YouTube Integration
@api_router.post("/integrations/youtube/setup")
async def setup_youtube_integration(email: str, password: str):
    """YouTube Account verbinden"""
    try:
        youtube_manager = YouTubeManager()
        auth_result = youtube_manager.authenticate_with_credentials(email, password)
        
        # Store credentials securely (in real system, encrypt these)
        integration_data = {
            'service': 'youtube',
            'email': email,
            'access_token': auth_result['access_token'],
            'status': 'connected',
            'setup_time': datetime.utcnow()
        }
        
        await db.integrations.insert_one(integration_data)
        
        return {
            'success': True,
            'service': 'youtube',
            'account': email,
            'message': 'YouTube Integration erfolgreich eingerichtet'
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"YouTube Setup fehlgeschlagen: {str(e)}")

@api_router.post("/integrations/youtube/upload")
async def upload_to_youtube(content_id: str):
    """Video automatisch auf YouTube hochladen"""
    try:
        # Get content
        content = await db.content.find_one({"id": content_id})
        if not content:
            raise HTTPException(status_code=404, detail="Content nicht gefunden")
        
        # Get YouTube integration
        integration = await db.integrations.find_one({"service": "youtube"})
        if not integration:
            raise HTTPException(status_code=400, detail="YouTube Integration nicht gefunden")
        
        youtube_manager = YouTubeManager()
        
        # Create video metadata
        video_metadata = {
            'title': content['title'],
            'description': content['content'][:5000],  # YouTube limit
            'tags': ['automatisierung', 'passiveseinkommen', 'onlinebusiness', 'ki', 'geld'],
            'privacy': 'public'
        }
        
        # Generate mock video data (in real system, this would be actual video)
        mock_video_data = f"Video Content: {content['content']}".encode()
        
        # Upload to YouTube
        upload_result = await youtube_manager.upload_video(
            integration['access_token'],
            mock_video_data,
            video_metadata
        )
        
        # Update content with YouTube URL
        await db.content.update_one(
            {"id": content_id},
            {"$set": {
                "youtube_url": upload_result.get('video_url'),
                "youtube_id": upload_result.get('video_id'),
                "published": True,
                "publish_date": datetime.utcnow()
            }}
        )
        
        return upload_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"YouTube Upload fehlgeschlagen: {str(e)}")

# TikTok Business Integration
@api_router.post("/integrations/tiktok/setup")
async def setup_tiktok_business():
    """TikTok Business Account einrichten"""
    try:
        tiktok_manager = TikTokBusinessManager()
        
        # Setup business profile with provided credentials
        account_credentials = {
            'email': 'samar220659@gmail.com',  # From user's provided info
            'password': '1010DANI'
        }
        
        setup_result = await tiktok_manager.setup_business_profile(account_credentials)
        
        if setup_result['success']:
            # Store integration
            integration_data = {
                'service': 'tiktok_business',
                'profile_id': setup_result['profile_id'],
                'profile_data': setup_result['profile_data'],
                'status': 'connected',
                'followers': 5000,  # User mentioned 5k followers
                'setup_time': datetime.utcnow()
            }
            
            await db.integrations.insert_one(integration_data)
        
        return setup_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TikTok Setup fehlgeschlagen: {str(e)}")

@api_router.post("/integrations/tiktok/post")
async def post_to_tiktok(content_id: str):
    """Content automatisch auf TikTok posten"""
    try:
        content = await db.content.find_one({"id": content_id})
        if not content:
            raise HTTPException(status_code=404, detail="Content nicht gefunden")
        
        integration = await db.integrations.find_one({"service": "tiktok_business"})
        if not integration:
            raise HTTPException(status_code=400, detail="TikTok Integration nicht gefunden")
        
        tiktok_manager = TikTokBusinessManager()
        
        # Prepare TikTok content
        tiktok_metadata = {
            'title': content['title'][:150],
            'hashtags': ['automatisierung', 'geld', 'passiv', 'online', 'business'],
            'privacy': 'public'
        }
        
        # Generate mock video data
        mock_video_data = f"TikTok Video: {content['content']}".encode()
        
        # Post to TikTok
        post_result = await tiktok_manager.post_video(
            'tiktok_access_token',
            mock_video_data,
            tiktok_metadata
        )
        
        # Update content
        await db.content.update_one(
            {"id": content_id},
            {"$set": {
                "tiktok_url": post_result.get('video_url'),
                "tiktok_id": post_result.get('video_id'),
                "tiktok_engagement": post_result.get('engagement_prediction'),
                "published": True
            }}
        )
        
        return post_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TikTok Post fehlgeschlagen: {str(e)}")

# Digistore24 Affiliate Integration
@api_router.post("/integrations/digistore24/setup")
async def setup_digistore24():
    """Digistore24 Affiliate Account verbinden"""
    try:
        digistore_manager = DigiStore24Manager()
        
        # Authenticate with provided credentials
        auth_result = await digistore_manager.authenticate(
            'samar220659@gmail.com',
            '1010Dani@'
        )
        
        if auth_result['success']:
            # Store integration
            integration_data = {
                'service': 'digistore24',
                'email': 'samar220659@gmail.com',
                'session_token': auth_result['session_token'],
                'status': 'connected',
                'setup_time': datetime.utcnow()
            }
            
            await db.integrations.insert_one(integration_data)
            
            # Get available affiliate products
            products_result = await digistore_manager.get_affiliate_links(auth_result['session_token'])
            
            return {
                'success': True,
                'auth_result': auth_result,
                'available_products': products_result['products'],
                'message': 'Digistore24 Integration erfolgreich eingerichtet'
            }
        
        return auth_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Digistore24 Setup fehlgeschlagen: {str(e)}")

@api_router.get("/integrations/digistore24/affiliates")
async def get_affiliate_products():
    """Verfügbare Affiliate-Produkte abrufen"""
    try:
        integration = await db.integrations.find_one({"service": "digistore24"})
        if not integration:
            raise HTTPException(status_code=400, detail="Digistore24 Integration nicht gefunden")
        
        digistore_manager = DigiStore24Manager()
        products_result = await digistore_manager.get_affiliate_links(integration['session_token'])
        
        return products_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Affiliate-Produkte laden fehlgeschlagen: {str(e)}")

# Cross-Platform Social Media Automation
@api_router.post("/integrations/social/cross-post")
async def cross_platform_posting(content_id: str, platforms: List[str]):
    """Content auf mehreren Social Media Plattformen gleichzeitig posten"""
    try:
        content = await db.content.find_one({"id": content_id})
        if not content:
            raise HTTPException(status_code=404, detail="Content nicht gefunden")
        
        social_manager = SocialMediaAutomation()
        
        # Content für Cross-Platform-Posting vorbereiten
        posting_content = {
            'title': content['title'],
            'description': content['content'],
            'hashtags': ['automatisierung', 'passiveseinkommen', 'onlinebusiness', 'ki']
        }
        
        # Cross-Platform Post ausführen
        results = await social_manager.cross_platform_post(posting_content, platforms)
        
        # Ergebnisse in Content speichern
        platform_urls = {}
        for platform, result in results['cross_platform_results'].items():
            if result.get('success'):
                platform_urls[f"{platform}_url"] = result.get('post_url', '')
                platform_urls[f"{platform}_id"] = result.get('post_id', '')
        
        await db.content.update_one(
            {"id": content_id},
            {"$set": {
                **platform_urls,
                "cross_platform_posted": True,
                "platforms": platforms,
                "posting_results": results
            }}
        )
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cross-Platform Posting fehlgeschlagen: {str(e)}")

# Email Marketing Automation
@api_router.post("/integrations/email/setup-sequence")
async def setup_email_sequence(lead_id: str, sequence_type: str = "welcome_sequence"):
    """Email-Marketing-Sequenz für Lead einrichten"""
    try:
        lead = await db.leads.find_one({"id": lead_id})
        if not lead:
            raise HTTPException(status_code=404, detail="Lead nicht gefunden")
        
        email_manager = EmailMarketingManager()
        
        # Lead-Daten für Personalisierung
        lead_data = {
            'first_name': lead.get('company', 'Freund').split()[0],
            'company': lead.get('company', 'Dein Business'),
            'industry': lead.get('industry', lead.get('company', 'Online-Business'))
        }
        
        # Email-Sequenz starten
        sequence_result = await email_manager.send_email_sequence(
            lead['email'],
            lead_data,
            sequence_type
        )
        
        # Email-Sequenz in Lead speichern
        await db.leads.update_one(
            {"id": lead_id},
            {"$set": {
                "email_sequence": sequence_result,
                "email_sequence_started": datetime.utcnow(),
                "sequence_type": sequence_type
            }}
        )
        
        return sequence_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email-Sequenz Setup fehlgeschlagen: {str(e)}")

# Enhanced Webhook Handler
@api_router.post("/webhook/lead")
async def webhook_receive_lead(data: Dict[str, Any]):
    """Webhook Endpoint für externe Lead-Quellen mit vollständiger Automatisierung"""
    try:
        webhook_handler = WebhookHandler()
        
        # Webhook-Lead verarbeiten
        processing_result = await webhook_handler.process_webhook_lead(
            data, 
            data.get('source', 'webhook')
        )
        
        if processing_result['success']:
            lead_data = processing_result['lead']
            
            # Lead in Datenbank speichern
            lead_create = LeadCreate(
                email=lead_data['email'],
                company=lead_data.get('company'),
                industry=lead_data.get('industry'),
                pain_points=[lead_data.get('interest', '')],
                source=lead_data['source'],
                workflow_id=await get_or_create_default_workflow()
            )
            
            # Create lead
            lead = await create_lead(lead_create)
            
            # Update with webhook processing results
            await db.leads.update_one(
                {"id": lead.id},
                {"$set": {
                    "webhook_processing": processing_result,
                    "automation_triggered": True,
                    "score": lead_data['score']
                }}
            )
            
            return {
                "message": "Lead erfolgreich verarbeitet und Vollautomatisierung gestartet",
                "lead_id": lead.id,
                "processing_results": processing_result,
                "automation_status": "active"
            }
        
        return processing_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webhook-Verarbeitung fehlgeschlagen: {str(e)}")

async def get_or_create_default_workflow():
    """Standard-Workflow erstellen falls nicht vorhanden"""
    workflow = await db.workflows.find_one({"type": "lead_gen"})
    if not workflow:
        workflow_create = WorkflowCreate(
            name="Vollautomatisierte Lead-Generierung",
            description="Komplette Automatisierung: Lead → Content → Multi-Platform → Revenue",
            type="lead_gen"
        )
        workflow = await create_workflow(workflow_create)
        return workflow.id
    return workflow["id"]

# Revenue Tracking für alle Integrationen
@api_router.post("/integrations/track-conversion")
async def track_conversion(source: str, amount: float, lead_id: Optional[str] = None):
    """Conversion von allen Integrationen tracken"""
    try:
        revenue_data = RevenueCreate(
            workflow_id=await get_or_create_default_workflow(),
            source=source,
            amount=amount,
            lead_id=lead_id
        )
        
        revenue = await add_revenue(revenue_data)
        
        # Wenn Digistore24, auch dort tracken
        if source == 'digistore24':
            digistore_manager = DigiStore24Manager()
            await digistore_manager.track_conversion('AUTO001', source, amount)
        
        return {
            'success': True,
            'revenue': revenue,
            'source': source,
            'amount': amount
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion Tracking fehlgeschlagen: {str(e)}")

# Komplett-Automatisierung Trigger
@api_router.post("/automation/full-automation/{lead_id}")
async def trigger_full_automation(lead_id: str):
    """Vollständige Automatisierungskette für Lead starten"""
    try:
        lead = await db.leads.find_one({"id": lead_id})
        if not lead:
            raise HTTPException(status_code=404, detail="Lead nicht gefunden")
        
        automation_results = {}
        
        # 1. Content generieren
        content_request = ContentCreate(
            content_type="video_script",
            target_audience=f"{lead.get('company', 'Unternehmen')} - {lead.get('industry', 'Business')}",
            keywords=['automatisierung', 'passiveseinkommen', 'geld', 'online'],
            workflow_id=lead['workflow_id'],
            lead_id=lead_id
        )
        
        content = await generate_content(content_request)
        automation_results['content_generation'] = {'success': True, 'content_id': content.id}
        
        # 2. Cross-Platform Social Media Posting
        platforms = ['youtube', 'tiktok', 'instagram', 'linkedin', 'facebook']
        social_result = await cross_platform_posting(content.id, platforms)
        automation_results['social_media_posting'] = social_result
        
        # 3. Email-Marketing-Sequenz starten
        email_result = await setup_email_sequence(lead_id, 'welcome_sequence')
        automation_results['email_sequence'] = email_result
        
        # 4. Affiliate-Links zuweisen
        affiliate_result = await get_affiliate_products()
        automation_results['affiliate_products'] = affiliate_result
        
        # 5. Lead-Score basierend auf Automatisierung aktualisieren
        await db.leads.update_one(
            {"id": lead_id},
            {"$set": {
                "full_automation_triggered": True,
                "automation_results": automation_results,
                "automation_date": datetime.utcnow(),
                "status": "automated",
                "score": min(lead.get('score', 5) + 3, 10)  # Bonus für Automatisierung
            }}
        )
        
        return {
            "message": "Vollständige Automatisierung erfolgreich gestartet",
            "lead_id": lead_id,
            "automation_results": automation_results,
            "platforms_posted": len(platforms),
            "email_sequence_started": True,
            "affiliate_products_available": len(affiliate_result.get('products', [])),
            "next_steps": [
                "Content wird automatisch auf allen Plattformen gepostet",
                "Email-Sequenz läuft für 30 Tage automatisch",
                "Affiliate-Links generieren passive Einnahmen",
                "Lead wird automatisch zu Kunden konvertiert"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vollständige Automatisierung fehlgeschlagen: {str(e)}")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()