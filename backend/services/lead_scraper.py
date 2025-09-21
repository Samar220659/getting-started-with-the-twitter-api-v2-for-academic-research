import asyncio
import random
from typing import List, Dict, Any
from datetime import datetime
from ..models.leads import LeadResult, SearchRecord

class MockLeadScraperService:
    """Mock service that simulates Google Maps scraping using Apify"""
    
    def __init__(self):
        self.mock_businesses = [
            {
                "businessName": "Tony's Pizzeria",
                "businessType": "Pizza Restaurant", 
                "phone": "(212) 555-0123",
                "website": "https://tonys-pizzeria.com",
                "email": "info@tonys-pizzeria.com",
                "rating": 4.5,
                "reviewCount": 267
            },
            {
                "businessName": "The Corner Bistro",
                "businessType": "American Restaurant",
                "phone": "(212) 555-0456", 
                "website": "https://cornerbistro.nyc",
                "email": "",
                "rating": 4.2,
                "reviewCount": 189
            },
            {
                "businessName": "Sakura Sushi",
                "businessType": "Japanese Restaurant",
                "phone": "(212) 555-0789",
                "website": "https://sakurasushi-nyc.com", 
                "email": "orders@sakurasushi-nyc.com",
                "rating": 4.7,
                "reviewCount": 342
            },
            {
                "businessName": "Maria's Tacos", 
                "businessType": "Mexican Restaurant",
                "phone": "(212) 555-0321",
                "website": "",
                "email": "",
                "rating": 4.3,
                "reviewCount": 156
            },
            {
                "businessName": "Blue Moon Cafe",
                "businessType": "Coffee Shop",
                "phone": "(212) 555-0654",
                "website": "https://bluemooncafe.com",
                "email": "hello@bluemooncafe.com", 
                "rating": 4.1,
                "reviewCount": 89
            },
            {
                "businessName": "Dragon Palace",
                "businessType": "Chinese Restaurant", 
                "phone": "(212) 555-0987",
                "website": "https://dragonpalace-nyc.com",
                "email": "",
                "rating": 4.4,
                "reviewCount": 203
            },
            {
                "businessName": "The Burger Joint",
                "businessType": "Burger Restaurant",
                "phone": "(212) 555-0147", 
                "website": "https://burgerjoint.com",
                "email": "contact@burgerjoint.com",
                "rating": 4.0,
                "reviewCount": 445
            },
            {
                "businessName": "Pasta La Vista", 
                "businessType": "Italian Restaurant",
                "phone": "(212) 555-0258",
                "website": "https://pasta-la-vista.com",
                "email": "",
                "rating": 4.6,
                "reviewCount": 178
            },
            {
                "businessName": "Spice Garden",
                "businessType": "Indian Restaurant",
                "phone": "(212) 555-0369",
                "website": "https://spicegarden-nyc.com", 
                "email": "info@spicegarden-nyc.com",
                "rating": 4.5,
                "reviewCount": 234
            },
            {
                "businessName": "Fresh & Green",
                "businessType": "Salad Bar",
                "phone": "(212) 555-0741",
                "website": "https://freshandgreen.com",
                "email": "orders@freshandgreen.com",
                "rating": 4.2,
                "reviewCount": 167
            }
        ]
    
    async def scrape_google_maps(self, search_request, search_id: str) -> List[LeadResult]:
        """Simulate Google Maps scraping with realistic delay"""
        
        # Simulate processing time (2-4 seconds)
        await asyncio.sleep(random.uniform(2, 4))
        
        # Generate realistic number of results
        max_results = min(search_request.maxResults, len(self.mock_businesses))
        num_results = random.randint(max(1, max_results - 5), max_results)
        
        results = []
        selected_businesses = random.sample(self.mock_businesses, num_results)
        
        for business in selected_businesses:
            # Modify business data based on search location
            address = self._generate_address(search_request.city, search_request.state, search_request.zipCode)
            phone = self._generate_phone(search_request.state)
            
            # Sometimes emails are missing (realistic scenario)
            email = business["email"] if random.random() > 0.3 else ""
            
            lead = LeadResult(
                businessName=business["businessName"],
                businessType=self._adapt_business_type(business["businessType"], search_request.query),
                address=address,
                phone=phone if random.random() > 0.1 else None,  # 10% chance of missing phone
                website=business["website"] if business["website"] else None,
                email=email if email else None,
                rating=round(random.uniform(3.5, 5.0), 1),
                reviewCount=random.randint(15, 500),
                searchId=search_id
            )
            results.append(lead)
        
        return results
    
    def _generate_address(self, city: str, state: str, zip_code: str = None) -> str:
        """Generate realistic address for the search location"""
        street_numbers = [random.randint(100, 9999) for _ in range(10)]
        street_names = [
            "Main St", "Broadway Ave", "Park Ave", "5th Street", "Columbus Circle",
            "Chinatown St", "Times Square", "Little Italy St", "Curry Lane", "Health St",
            "Wall Street", "Soho St", "Harbor View", "Green Ave", "Smoke Street"
        ]
        
        street_number = random.choice(street_numbers)
        street_name = random.choice(street_names)
        
        if zip_code:
            return f"{street_number} {street_name}, {city}, {state} {zip_code}"
        else:
            # Generate random zip for the state
            zip_codes = {"NY": "10001", "CA": "90210", "TX": "78701", "FL": "33101"}
            default_zip = zip_codes.get(state, "12345")
            return f"{street_number} {street_name}, {city}, {state} {default_zip}"
    
    def _generate_phone(self, state: str) -> str:
        """Generate realistic phone number for the state"""
        area_codes = {
            "NY": ["212", "646", "917"],
            "CA": ["213", "310", "415"], 
            "TX": ["214", "713", "512"],
            "FL": ["305", "407", "813"]
        }
        
        area_code = random.choice(area_codes.get(state, ["555"]))
        number = f"({area_code}) {random.randint(100, 999)}-{random.randint(1000, 9999)}"
        return number
    
    def _adapt_business_type(self, original_type: str, query: str) -> str:
        """Adapt business type based on search query"""
        query_lower = query.lower()
        
        if "restaurant" in query_lower or "food" in query_lower:
            return original_type
        elif "plumber" in query_lower:
            return "Plumbing Service"
        elif "salon" in query_lower or "hair" in query_lower:
            return "Hair Salon"
        elif "gym" in query_lower or "fitness" in query_lower:
            return "Fitness Center"
        elif "dental" in query_lower or "dentist" in query_lower:
            return "Dental Clinic"
        else:
            return original_type


class MockEmailEnrichmentService:
    """Mock service that simulates Hunter.io email enrichment"""
    
    def __init__(self):
        self.mock_emails = [
            "contact@{domain}",
            "info@{domain}", 
            "hello@{domain}",
            "owner@{domain}",
            "admin@{domain}",
            "support@{domain}"
        ]
    
    async def enrich_email(self, website: str) -> str:
        """Simulate email enrichment with realistic delay"""
        
        # Simulate processing time (1-3 seconds)
        await asyncio.sleep(random.uniform(1, 3))
        
        # Extract domain from website URL
        try:
            if "://" in website:
                domain = website.split("://")[1]
            else:
                domain = website
                
            if "/" in domain:
                domain = domain.split("/")[0]
                
            # Remove www. if present
            if domain.startswith("www."):
                domain = domain[4:]
                
            # 70% success rate for finding emails
            if random.random() < 0.7:
                email_template = random.choice(self.mock_emails)
                return email_template.format(domain=domain)
            else:
                return None
                
        except Exception:
            return None