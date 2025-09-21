from celery_app import celery_app
from tasks.base_scraper import BaseScraper
import asyncio
import logging

logger = logging.getLogger(__name__)

class FinanceDataCollector(BaseScraper):
    """Finance & Investment Data Collector Task"""
    pass

@celery_app.task(bind=True, base=FinanceDataCollector)
def collect_finance_data(self, search_params):
    """Automatisierte Finanzdaten-Sammlung"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        task_id = loop.run_until_complete(
            self.log_task_start("finance_data_collector", search_params)
        )
        
        # Realistische Verzögerung
        self.simulate_realistic_delay(1.0, 3.0)
        
        # Mock-Daten generieren
        finance_data = self.generate_mock_data("finance_data_collector", search_params.get('max_stocks', 15))
        
        # Ergebnisse speichern
        loop.run_until_complete(
            self.store_results("financial_instruments", task_id, finance_data)
        )
        
        loop.run_until_complete(
            self.log_task_completion(task_id, finance_data, success=True)
        )
        
        logger.info(f"Finanzdaten-Sammlung erfolgreich: {len(finance_data)} Instrumente analysiert")
        
        return {
            'success': True,
            'task_id': task_id,
            'instruments_count': len(finance_data),
            'instruments': finance_data,
            'message': f"Erfolgreich {len(finance_data)} Finanzinstrumente analysiert"
        }
        
    except Exception as e:
        logger.error(f"Finanzdaten-Sammlung fehlgeschlagen: {str(e)}")
        raise self.retry(exc=e, countdown=60, max_retries=3)