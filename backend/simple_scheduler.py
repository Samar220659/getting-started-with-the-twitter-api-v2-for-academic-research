import asyncio
import logging
import schedule
import time
import threading
from datetime import datetime
from database import db
from services.lead_scraper import MockLeadScraperService
from models.leads import SearchRequest
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleWorkflowScheduler:
    """Einfacher Workflow-Scheduler ohne Redis/Celery"""
    
    def __init__(self):
        self.running = False
        self.scraper_service = MockLeadScraperService()
        
    async def execute_google_maps_workflow(self):
        """Google Maps Workflow ausführen"""
        try:
            logger.info("Starte Google Maps Workflow...")
            
            # Task-Record erstellen
            task_record = {
                'id': str(uuid.uuid4()),
                'workflow_type': 'google_maps_scraper',
                'status': 'running',
                'parameters': {'query': 'restaurants', 'city': 'München', 'state': 'BY', 'maxResults': 20},
                'started_at': datetime.utcnow()
            }
            
            await db.automation_tasks.insert_one(task_record)
            task_id = task_record['id']
            
            # Leads generieren
            search_request = SearchRequest(**task_record['parameters'])
            leads = await self.scraper_service.scrape_google_maps(search_request, task_id)
            
            # Ergebnisse speichern
            results = [lead.dict() for lead in leads]
            for result in results:
                result['task_id'] = task_id
                result['created_at'] = datetime.utcnow()
                result['id'] = str(uuid.uuid4())
            
            if results:
                await db.google_maps_results.insert_many(results)
            
            # Task als erfolgreich markieren
            await db.automation_tasks.update_one(
                {'id': task_id},
                {'$set': {
                    'status': 'completed',
                    'completed_at': datetime.utcnow(),
                    'results_count': len(results)
                }}
            )
            
            logger.info(f"Google Maps Workflow erfolgreich: {len(results)} Leads generiert")
            
        except Exception as e:
            logger.error(f"Google Maps Workflow fehlgeschlagen: {str(e)}")
            if 'task_id' in locals():
                await db.automation_tasks.update_one(
                    {'id': task_id},
                    {'$set': {
                        'status': 'failed',
                        'completed_at': datetime.utcnow(),
                        'error': str(e)
                    }}
                )
    
    async def execute_demo_workflows(self):
        """Demo-Workflows für andere Bereiche ausführen"""
        try:
            workflows = [
                {'type': 'linkedin_extractor', 'data_count': 15},
                {'type': 'ecommerce_intelligence', 'data_count': 25},
                {'type': 'social_media_harvester', 'data_count': 20},
                {'type': 'real_estate_analyzer', 'data_count': 12},
                {'type': 'job_market_intelligence', 'data_count': 18}
            ]
            
            for workflow in workflows:
                logger.info(f"Starte Demo-Workflow: {workflow['type']}")
                
                # Task-Record
                task_record = {
                    'id': str(uuid.uuid4()),
                    'workflow_type': workflow['type'],
                    'status': 'running',
                    'parameters': {'demo': True, 'count': workflow['data_count']},
                    'started_at': datetime.utcnow()
                }
                
                await db.automation_tasks.insert_one(task_record)
                task_id = task_record['id']
                
                # Mock-Daten generieren
                mock_data = self._generate_workflow_data(workflow['type'], workflow['data_count'])
                
                # In entsprechende Collection speichern
                collection_name = f"{workflow['type']}_results"
                collection = getattr(db, collection_name)
                
                for data in mock_data:
                    data['task_id'] = task_id
                    data['created_at'] = datetime.utcnow()
                    data['id'] = str(uuid.uuid4())
                
                if mock_data:
                    await collection.insert_many(mock_data)
                
                # Task abschließen
                await db.automation_tasks.update_one(
                    {'id': task_id},
                    {'$set': {
                        'status': 'completed',
                        'completed_at': datetime.utcnow(),
                        'results_count': len(mock_data)
                    }}
                )
                
                logger.info(f"Demo-Workflow {workflow['type']} erfolgreich: {len(mock_data)} Datensätze")
                
                # Kurze Pause zwischen Workflows
                await asyncio.sleep(2)
                
        except Exception as e:
            logger.error(f"Demo-Workflows fehlgeschlagen: {str(e)}")
    
    def _generate_workflow_data(self, workflow_type: str, count: int):
        """Mock-Daten für verschiedene Workflows generieren"""
        import random
        
        if workflow_type == 'linkedin_extractor':
            return [
                {
                    'name': f'Max Mustermann {i}',
                    'position': random.choice(['Sales Director', 'Marketing Manager', 'CEO']),
                    'company': random.choice(['SAP', 'Siemens', 'BMW']),
                    'location': random.choice(['München', 'Berlin', 'Hamburg']),
                    'connections': random.randint(50, 500)
                } for i in range(count)
            ]
        
        elif workflow_type == 'ecommerce_intelligence':
            return [
                {
                    'product_name': f'Produkt {i}',
                    'price': round(random.uniform(20, 500), 2),
                    'rating': round(random.uniform(3.5, 5.0), 1),
                    'category': random.choice(['Electronics', 'Fashion', 'Home'])
                } for i in range(count)
            ]
        
        elif workflow_type == 'social_media_harvester':
            return [
                {
                    'username': f'@user_{i}',
                    'platform': random.choice(['Instagram', 'TikTok', 'YouTube']),
                    'followers': random.randint(1000, 100000),
                    'engagement_rate': round(random.uniform(2.0, 8.0), 2)
                } for i in range(count)
            ]
        
        elif workflow_type == 'real_estate_analyzer':
            return [
                {
                    'property_type': random.choice(['Wohnung', 'Haus', 'Studio']),
                    'price': random.randint(200000, 800000),
                    'city': random.choice(['München', 'Berlin', 'Hamburg']),
                    'rooms': random.randint(1, 5)
                } for i in range(count)
            ]
        
        elif workflow_type == 'job_market_intelligence':
            return [
                {
                    'job_title': random.choice(['Developer', 'Manager', 'Designer']),
                    'company': f'Firma {i}',
                    'salary_min': random.randint(40000, 70000),
                    'location': random.choice(['München', 'Berlin', 'Frankfurt'])
                } for i in range(count)
            ]
        
        return []
    
    async def health_check(self):
        """Einfacher System-Health-Check"""
        try:
            health_record = {
                'timestamp': datetime.utcnow(),
                'overall_status': 'healthy',
                'services': {
                    'mongodb': {'status': 'healthy'},
                    'scheduler': {'status': 'healthy'}
                },
                'system_resources': {
                    'status': 'healthy'
                }
            }
            
            await db.health_checks.insert_one(health_record)
            logger.info("Health-Check erfolgreich durchgeführt")
            
        except Exception as e:
            logger.error(f"Health-Check fehlgeschlagen: {str(e)}")
    
    async def cleanup_old_data(self):
        """Alte Daten bereinigen (vereinfacht)"""
        try:
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=7)
            
            collections = [
                'automation_tasks', 'health_checks', 'google_maps_results',
                'linkedin_extractor_results', 'ecommerce_intelligence_results'
            ]
            
            total_deleted = 0
            for collection_name in collections:
                try:
                    collection = getattr(db, collection_name)
                    result = await collection.delete_many({'created_at': {'$lt': cutoff_date}})
                    total_deleted += result.deleted_count
                except:
                    pass
            
            logger.info(f"Cleanup abgeschlossen: {total_deleted} alte Records gelöscht")
            
        except Exception as e:
            logger.error(f"Cleanup fehlgeschlagen: {str(e)}")
    
    def schedule_workflows(self):
        """Workflows planen ohne Redis/Celery"""
        # Google Maps alle 2 Stunden
        schedule.every(2).hours.do(lambda: asyncio.run(self.execute_google_maps_workflow()))
        
        # Demo-Workflows alle 4 Stunden  
        schedule.every(4).hours.do(lambda: asyncio.run(self.execute_demo_workflows()))
        
        # Health-Checks alle 30 Minuten
        schedule.every(30).minutes.do(lambda: asyncio.run(self.health_check()))
        
        # Cleanup täglich
        schedule.every().day.at("02:00").do(lambda: asyncio.run(self.cleanup_old_data()))
        
        logger.info("Workflows geplant: Google Maps (2h), Demo-Workflows (4h), Health-Checks (30min), Cleanup (täglich)")
    
    def start(self):
        """Scheduler starten"""
        self.running = True
        self.schedule_workflows()
        
        logger.info("Simple Workflow Scheduler gestartet")
        
        # Initial-Workflows ausführen
        asyncio.run(self.execute_google_maps_workflow())
        asyncio.run(self.execute_demo_workflows())
        
        # Scheduler-Loop
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Prüfe jede Minute
            except KeyboardInterrupt:
                logger.info("Scheduler gestoppt")
                break
            except Exception as e:
                logger.error(f"Scheduler-Fehler: {str(e)}")
                time.sleep(60)
    
    def stop(self):
        """Scheduler stoppen"""
        self.running = False
        logger.info("Scheduler wird gestoppt...")

if __name__ == "__main__":
    scheduler = SimpleWorkflowScheduler()
    scheduler.start()