from celery_app import celery_app
from tasks.base_scraper import BaseScraper
import asyncio
from services.lead_scraper import MockLeadScraperService
from models.leads import SearchRequest
import logging

logger = logging.getLogger(__name__)

class GoogleMapsScraper(BaseScraper):
    """Google Maps Lead Scraping Task"""
    pass

@celery_app.task(bind=True, base=GoogleMapsScraper)
def scrape_google_maps_leads(self, search_params):
    """Automatisierte Google Maps Lead-Extraktion"""
    try:
        # Event loop für async Funktionen
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Task in DB loggen
        task_id = loop.run_until_complete(
            self.log_task_start("google_maps_scraper", search_params)
        )
        
        # Realistische Verzögerung
        self.simulate_realistic_delay(2.0, 4.0)
        
        # Lead Scraping Service
        scraper_service = MockLeadScraperService()
        search_request = SearchRequest(**search_params)
        
        # Leads extrahieren
        leads = loop.run_until_complete(
            scraper_service.scrape_google_maps(search_request, task_id)
        )
        
        # Ergebnisse in DB speichern
        results = [lead.dict() for lead in leads]
        loop.run_until_complete(
            self.store_results("google_maps", task_id, results)
        )
        
        # Task als erfolgreich markieren
        loop.run_until_complete(
            self.log_task_completion(task_id, results, success=True)
        )
        
        logger.info(f"Google Maps Scraping erfolgreich: {len(results)} Leads extrahiert")
        
        return {
            'success': True,
            'task_id': task_id,
            'leads_count': len(results),
            'leads': results,
            'message': f"Erfolgreich {len(results)} Leads für '{search_params.get('query')}' extrahiert"
        }
        
    except Exception as e:
        logger.error(f"Google Maps Scraping fehlgeschlagen: {str(e)}")
        
        # Task als fehlgeschlagen markieren
        if 'task_id' in locals():
            loop.run_until_complete(
                self.log_task_completion(task_id, [], success=False)
            )
        
        # Task retry
        raise self.retry(exc=e, countdown=60, max_retries=3)

@celery_app.task(bind=True, base=GoogleMapsScraper)
def auto_generate_demo_leads(self):
    """Automatische Demo-Lead-Generierung für Showcase"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Demo-Parameter
        demo_params = {
            'query': 'restaurants',
            'city': 'München', 
            'state': 'BY',
            'maxResults': 15
        }
        
        task_id = loop.run_until_complete(
            self.log_task_start("auto_demo_leads", demo_params)
        )
        
        # Demo-Leads generieren
        leads_data = self.generate_mock_data("google_maps", 15)
        
        # In spezielle Demo-Collection speichern
        loop.run_until_complete(
            self.store_results("demo_leads", task_id, leads_data)
        )
        
        loop.run_until_complete(
            self.log_task_completion(task_id, leads_data, success=True)
        )
        
        logger.info(f"Demo-Leads automatisch generiert: {len(leads_data)} Leads")
        
        return {
            'success': True,
            'task_id': task_id,
            'demo_leads': len(leads_data)
        }
        
    except Exception as e:
        logger.error(f"Demo-Lead-Generierung fehlgeschlagen: {str(e)}")
        raise self.retry(exc=e, countdown=300, max_retries=2)

@celery_app.task(bind=True, base=GoogleMapsScraper)  
def batch_process_multiple_searches(self, search_list):
    """Batch-Verarbeitung mehrerer Suchanfragen"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        task_id = loop.run_until_complete(
            self.log_task_start("batch_google_maps", {'searches': len(search_list)})
        )
        
        all_results = []
        
        for search_params in search_list:
            # Jede Suche einzeln verarbeiten
            result = scrape_google_maps_leads.apply_async(args=[search_params])
            search_result = result.get(timeout=300)  # 5 Minuten Timeout
            
            if search_result['success']:
                all_results.extend(search_result['leads'])
            
            # Pause zwischen Suchen
            self.simulate_realistic_delay(1.0, 2.0)
        
        loop.run_until_complete(
            self.log_task_completion(task_id, all_results, success=True)
        )
        
        logger.info(f"Batch-Verarbeitung erfolgreich: {len(all_results)} Gesamt-Leads")
        
        return {
            'success': True,
            'task_id': task_id,
            'total_leads': len(all_results),
            'searches_processed': len(search_list)
        }
        
    except Exception as e:
        logger.error(f"Batch-Verarbeitung fehlgeschlagen: {str(e)}")
        raise self.retry(exc=e, countdown=120, max_retries=2)