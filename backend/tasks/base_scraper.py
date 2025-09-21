from celery import Task
import asyncio
import logging
from datetime import datetime
from database import db
import uuid
from typing import Dict, List, Any
import random
import time

logger = logging.getLogger(__name__)

class BaseScraper(Task):
    """Basis-Klasse für alle Scraping-Tasks"""
    
    def __init__(self):
        self.max_retries = 3
        self.default_retry_delay = 60
        self.rate_limit = '10/m'  # 10 Requests pro Minute
        
    async def log_task_start(self, workflow_type: str, params: Dict[str, Any]) -> str:
        """Task-Start in Database loggen"""
        task_record = {
            'id': str(uuid.uuid4()),
            'workflow_type': workflow_type,
            'status': 'running',
            'parameters': params,
            'started_at': datetime.utcnow(),
            'celery_task_id': self.request.id if hasattr(self, 'request') else None
        }
        
        await db.automation_tasks.insert_one(task_record)
        logger.info(f"Task {workflow_type} gestartet: {task_record['id']}")
        return task_record['id']
        
    async def log_task_completion(self, task_id: str, results: List[Dict[str, Any]], success: bool = True):
        """Task-Completion in Database loggen"""
        update_data = {
            'status': 'completed' if success else 'failed',
            'completed_at': datetime.utcnow(),
            'results_count': len(results) if results else 0,
            'results': results[:10] if results else []  # Nur erste 10 für Logging
        }
        
        await db.automation_tasks.update_one(
            {'id': task_id},
            {'$set': update_data}
        )
        
        logger.info(f"Task {task_id} {'erfolgreich' if success else 'fehlgeschlagen'}: {len(results) if results else 0} Ergebnisse")
        
    def simulate_realistic_delay(self, min_delay: float = 2.0, max_delay: float = 5.0):
        """Realistische Verzögerung für Scraping-Simulation"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
        logger.debug(f"Scraping-Verzögerung: {delay:.2f}s")
        
    async def store_results(self, workflow_type: str, task_id: str, results: List[Dict[str, Any]]):
        """Ergebnisse in spezifischer Collection speichern"""
        if not results:
            return
            
        collection_name = f"{workflow_type}_results"
        collection = getattr(db, collection_name)
        
        # Füge Task-ID und Timestamp hinzu
        for result in results:
            result['task_id'] = task_id
            result['created_at'] = datetime.utcnow()
            result['id'] = str(uuid.uuid4())
            
        await collection.insert_many(results)
        logger.info(f"{len(results)} Ergebnisse in {collection_name} gespeichert")
        
    def generate_mock_data(self, workflow_type: str, count: int = 10) -> List[Dict[str, Any]]:
        """Mock-Daten für verschiedene Workflows generieren"""
        
        if workflow_type == "linkedin_extractor":
            return self._generate_linkedin_data(count)
        elif workflow_type == "ecommerce_intelligence":
            return self._generate_ecommerce_data(count)
        elif workflow_type == "social_media_harvester":
            return self._generate_social_media_data(count)
        elif workflow_type == "real_estate_analyzer":
            return self._generate_real_estate_data(count)
        elif workflow_type == "job_market_intelligence":
            return self._generate_job_market_data(count)
        elif workflow_type == "restaurant_analyzer":
            return self._generate_restaurant_data(count)
        elif workflow_type == "finance_data_collector":
            return self._generate_finance_data(count)
        elif workflow_type == "event_scout":
            return self._generate_event_data(count)
        elif workflow_type == "vehicle_market_intel":
            return self._generate_vehicle_data(count)
        elif workflow_type == "seo_opportunity_finder":
            return self._generate_seo_data(count)
        else:
            return []
            
    def _generate_linkedin_data(self, count: int) -> List[Dict[str, Any]]:
        """LinkedIn Profile Mock-Daten"""
        names = ["Max Mustermann", "Anna Schmidt", "Thomas Weber", "Sarah König", "Michael Fischer"]
        positions = ["Sales Director", "Marketing Manager", "CEO", "CTO", "Head of Operations"]
        companies = ["SAP", "Siemens", "BMW", "Deutsche Bank", "Allianz"]
        
        results = []
        for i in range(count):
            result = {
                'name': random.choice(names),
                'position': random.choice(positions),
                'company': random.choice(companies),
                'location': random.choice(["München", "Berlin", "Hamburg", "Frankfurt", "Köln"]),
                'connections': random.randint(50, 500),
                'email': f"{random.choice(names).lower().replace(' ', '.')}@{random.choice(companies).lower()}.com",
                'linkedin_url': f"https://linkedin.com/in/{random.choice(names).lower().replace(' ', '-')}",
                'industry': random.choice(["Technology", "Finance", "Automotive", "Healthcare", "Manufacturing"])
            }
            results.append(result)
        return results
        
    def _generate_ecommerce_data(self, count: int) -> List[Dict[str, Any]]:
        """E-Commerce Produkt Mock-Daten"""
        products = ["iPhone 15", "Samsung Galaxy S24", "MacBook Pro", "Dell XPS", "iPad Air"]
        categories = ["Smartphones", "Laptops", "Tablets", "Accessories", "Gaming"]
        
        results = []
        for i in range(count):
            price = random.randint(200, 2000)
            result = {
                'product_name': random.choice(products),
                'category': random.choice(categories),
                'price': price,
                'original_price': price + random.randint(50, 300),
                'discount_percentage': random.randint(5, 40),
                'rating': round(random.uniform(3.5, 5.0), 1),
                'reviews_count': random.randint(10, 1000),
                'seller': random.choice(["Amazon", "MediaMarkt", "Saturn", "Otto", "Zalando"]),
                'availability': random.choice(["In Stock", "Limited", "Pre-order"]),
                'url': f"https://shop.example.com/product/{i}"
            }
            results.append(result)
        return results
        
    def _generate_social_media_data(self, count: int) -> List[Dict[str, Any]]:
        """Social Media Influencer Mock-Daten"""
        usernames = ["@lifestyle_guru", "@tech_reviewer", "@food_blogger", "@fitness_coach", "@travel_expert"]
        platforms = ["Instagram", "TikTok", "YouTube", "Twitter", "LinkedIn"]
        
        results = []
        for i in range(count):
            followers = random.randint(1000, 1000000)
            result = {
                'username': random.choice(usernames),
                'platform': random.choice(platforms),
                'followers': followers,
                'following': random.randint(100, 5000),
                'posts_count': random.randint(50, 2000),
                'engagement_rate': round(random.uniform(1.5, 8.0), 2),
                'avg_likes': int(followers * random.uniform(0.02, 0.15)),
                'avg_comments': int(followers * random.uniform(0.005, 0.03)),
                'category': random.choice(["Lifestyle", "Technology", "Food", "Fitness", "Travel"]),
                'verified': random.choice([True, False])
            }
            results.append(result)
        return results
        
    def _generate_real_estate_data(self, count: int) -> List[Dict[str, Any]]:
        """Immobilien Mock-Daten"""
        property_types = ["Wohnung", "Haus", "Penthouse", "Studio", "Loft"]
        cities = ["München", "Berlin", "Hamburg", "Frankfurt", "Stuttgart"]
        
        results = []
        for i in range(count):
            price = random.randint(200000, 2000000)
            result = {
                'property_type': random.choice(property_types),
                'city': random.choice(cities),
                'district': f"Stadtteil {i+1}",
                'price': price,
                'price_per_sqm': price // random.randint(50, 150),
                'rooms': random.randint(1, 6),
                'size_sqm': random.randint(30, 200),
                'year_built': random.randint(1960, 2024),
                'energy_rating': random.choice(["A+", "A", "B", "C", "D"]),
                'for_sale': random.choice([True, False]),
                'balcony': random.choice([True, False]),
                'parking': random.choice([True, False])
            }
            results.append(result)
        return results
        
    def _generate_job_market_data(self, count: int) -> List[Dict[str, Any]]:
        """Job-Markt Mock-Daten"""
        job_titles = ["Software Developer", "Product Manager", "Data Scientist", "UX Designer", "Sales Manager"]
        companies = ["Google", "Microsoft", "Amazon", "SAP", "Zalando"]
        
        results = []
        for i in range(count):
            salary_min = random.randint(40000, 80000)
            result = {
                'job_title': random.choice(job_titles),
                'company': random.choice(companies),
                'location': random.choice(["München", "Berlin", "Hamburg", "Frankfurt", "Köln"]),
                'salary_min': salary_min,
                'salary_max': salary_min + random.randint(10000, 40000),
                'experience_level': random.choice(["Junior", "Mid", "Senior", "Lead"]),
                'remote_possible': random.choice([True, False]),
                'contract_type': random.choice(["Vollzeit", "Teilzeit", "Freelance"]),
                'posted_days_ago': random.randint(1, 30),
                'applications': random.randint(5, 200)
            }
            results.append(result)
        return results
        
    def _generate_restaurant_data(self, count: int) -> List[Dict[str, Any]]:
        """Restaurant Mock-Daten"""
        cuisines = ["Italienisch", "Deutsch", "Asiatisch", "Französisch", "Amerikanisch"]
        cities = ["München", "Berlin", "Hamburg", "Frankfurt", "Köln"]
        
        results = []
        for i in range(count):
            result = {
                'name': f"Restaurant {i+1}",
                'cuisine': random.choice(cuisines),
                'city': random.choice(cities),
                'rating': round(random.uniform(3.0, 5.0), 1),
                'review_count': random.randint(20, 500),
                'price_range': random.choice(["€", "€€", "€€€", "€€€€"]),
                'delivery_available': random.choice([True, False]),
                'reservation_required': random.choice([True, False]),
                'opening_hours': "11:00-23:00",
                'phone': f"+49 89 {random.randint(1000000, 9999999)}",
                'address': f"Straße {i+1}, {random.choice(cities)}"
            }
            results.append(result)
        return results
        
    def _generate_finance_data(self, count: int) -> List[Dict[str, Any]]:
        """Finanz Mock-Daten"""
        symbols = ["BMW", "SAP", "SIEMENS", "ALLIANZ", "DEUTSCHE_BANK"]
        
        results = []
        for i in range(count):
            price = random.uniform(50, 500)
            result = {
                'symbol': random.choice(symbols),
                'company_name': f"{random.choice(symbols)} AG",
                'current_price': round(price, 2),
                'price_change': round(random.uniform(-5, 5), 2),
                'price_change_percent': round(random.uniform(-10, 10), 2),
                'volume': random.randint(100000, 10000000),
                'market_cap': random.randint(1000000000, 100000000000),
                'pe_ratio': round(random.uniform(10, 30), 2),
                'dividend_yield': round(random.uniform(1, 5), 2),
                'sector': random.choice(["Technology", "Finance", "Automotive", "Healthcare", "Industrial"])
            }
            results.append(result)
        return results
        
    def _generate_event_data(self, count: int) -> List[Dict[str, Any]]:
        """Event Mock-Daten"""
        event_types = ["Konferenz", "Konzert", "Workshop", "Messe", "Networking"]
        cities = ["München", "Berlin", "Hamburg", "Frankfurt", "Köln"]
        
        results = []
        for i in range(count):
            ticket_price = random.randint(20, 500)
            result = {
                'event_name': f"{random.choice(event_types)} {i+1}",
                'event_type': random.choice(event_types),
                'city': random.choice(cities),
                'date': f"2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                'venue': f"Location {i+1}",
                'ticket_price': ticket_price,
                'tickets_available': random.randint(0, 1000),
                'organizer': f"Veranstalter {i+1}",
                'category': random.choice(["Business", "Entertainment", "Education", "Technology", "Arts"]),
                'duration_hours': random.randint(2, 8)
            }
            results.append(result)
        return results
        
    def _generate_vehicle_data(self, count: int) -> List[Dict[str, Any]]:
        """Fahrzeug Mock-Daten"""
        brands = ["BMW", "Mercedes", "Audi", "VW", "Porsche"]
        models = ["A4", "C-Class", "3er", "Golf", "911"]
        
        results = []
        for i in range(count):
            price = random.randint(15000, 80000)
            result = {
                'brand': random.choice(brands),
                'model': random.choice(models),
                'year': random.randint(2015, 2024),
                'price': price,
                'mileage': random.randint(10000, 200000),
                'fuel_type': random.choice(["Benzin", "Diesel", "Elektro", "Hybrid"]),
                'transmission': random.choice(["Automatik", "Manuell"]),
                'color': random.choice(["Schwarz", "Weiß", "Silber", "Rot", "Blau"]),
                'condition': random.choice(["Neu", "Sehr gut", "Gut", "Gebraucht"]),
                'seller_type': random.choice(["Händler", "Privat"])
            }
            results.append(result)
        return results
        
    def _generate_seo_data(self, count: int) -> List[Dict[str, Any]]:
        """SEO Opportunity Mock-Daten"""
        keywords = ["digitales marketing", "online shop", "seo beratung", "web entwicklung", "social media"]
        
        results = []
        for i in range(count):
            result = {
                'keyword': random.choice(keywords),
                'search_volume': random.randint(100, 50000),
                'keyword_difficulty': random.randint(10, 90),
                'cpc': round(random.uniform(0.5, 10.0), 2),
                'competition': random.choice(["Low", "Medium", "High"]),
                'trend': random.choice(["Rising", "Stable", "Declining"]),
                'related_keywords': [f"related {i}", f"similar {i}", f"alternative {i}"],
                'serp_features': random.choice(["Featured Snippet", "People Also Ask", "Images", "Videos"]),
                'opportunity_score': random.randint(1, 100)
            }
            results.append(result)
        return results