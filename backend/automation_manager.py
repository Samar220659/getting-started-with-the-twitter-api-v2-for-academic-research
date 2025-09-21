#!/usr/bin/env python3
"""
LeadMaps Automation Manager
Autonomer Dauerbetrieb aller Workflows mit Health-Monitoring
"""

import os
import sys
import time
import logging
import signal
import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import redis
from celery_app import celery_app

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/automation_manager.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class AutomationManager:
    """Hauptklasse für Workflow-Automatisierung"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.running = False
        self.redis_client = None
        self.workflows_config = self._load_workflows_config()
        
        # Signal Handler für graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Graceful Shutdown Handler"""
        logger.info(f"Signal {signum} empfangen - Starte Shutdown...")
        self.stop()
        
    def _load_workflows_config(self):
        """Workflow-Konfigurationen laden"""
        return {
            'google_maps_scraper': {
                'enabled': True,
                'schedule': 'interval',
                'interval_minutes': 60,
                'params': {
                    'query': 'restaurants',
                    'city': 'München',
                    'state': 'BY',
                    'maxResults': 20
                }
            },
            'linkedin_extractor': {
                'enabled': True,
                'schedule': 'interval', 
                'interval_minutes': 180,
                'params': {
                    'search_terms': ['sales manager', 'marketing director'],
                    'location': 'Deutschland',
                    'max_results': 25
                }
            },
            'ecommerce_intelligence': {
                'enabled': True,
                'schedule': 'interval',
                'interval_minutes': 120,
                'params': {
                    'categories': ['smartphones', 'laptops'],
                    'max_products': 30
                }
            },
            'social_media_harvester': {
                'enabled': True,
                'schedule': 'interval',
                'interval_minutes': 240,
                'params': {
                    'platforms': ['instagram', 'tiktok'],
                    'categories': ['lifestyle', 'tech'],
                    'max_accounts': 20
                }
            },
            'real_estate_analyzer': {
                'enabled': True,
                'schedule': 'cron',
                'cron': '0 */6 * * *',  # Alle 6 Stunden
                'params': {
                    'cities': ['München', 'Berlin', 'Hamburg'],
                    'property_types': ['wohnung', 'haus'],
                    'max_properties': 15
                }
            },
            'job_market_intelligence': {
                'enabled': True,
                'schedule': 'cron',
                'cron': '0 8 * * *',  # Täglich um 8 Uhr
                'params': {
                    'job_titles': ['software developer', 'data scientist'],
                    'locations': ['München', 'Berlin'],
                    'max_jobs': 25
                }
            },
            'restaurant_analyzer': {
                'enabled': True,
                'schedule': 'interval',
                'interval_minutes': 360,
                'params': {
                    'cities': ['München', 'Berlin'],
                    'cuisines': ['italienisch', 'asiatisch'],
                    'max_restaurants': 20
                }
            },
            'finance_data_collector': {
                'enabled': True,
                'schedule': 'interval',
                'interval_minutes': 30,
                'params': {
                    'symbols': ['BMW', 'SAP', 'SIEMENS'],
                    'max_stocks': 15
                }
            },
            'event_scout': {
                'enabled': True,
                'schedule': 'cron',
                'cron': '0 9 * * *',  # Täglich um 9 Uhr
                'params': {
                    'cities': ['München', 'Berlin'],
                    'categories': ['business', 'technology'],
                    'max_events': 18
                }
            },
            'vehicle_market_intel': {
                'enabled': True,
                'schedule': 'cron', 
                'cron': '0 */12 * * *',  # Alle 12 Stunden
                'params': {
                    'brands': ['BMW', 'Mercedes', 'Audi'],
                    'max_vehicles': 12
                }
            },
            'seo_opportunity_finder': {
                'enabled': True,
                'schedule': 'cron',
                'cron': '0 10 * * *',  # Täglich um 10 Uhr
                'params': {
                    'industries': ['marketing', 'ecommerce'],
                    'max_keywords': 30
                }
            }
        }
    
    def initialize_redis(self):
        """Redis-Verbindung initialisieren"""
        try:
            self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            self.redis_client.ping()
            logger.info("Redis-Verbindung erfolgreich initialisiert")
            return True
        except Exception as e:
            logger.error(f"Redis-Initialisierung fehlgeschlagen: {str(e)}")
            return False
    
    def schedule_workflows(self):
        """Alle Workflows nach Konfiguration planen"""
        for workflow_name, config in self.workflows_config.items():
            if not config.get('enabled', False):
                logger.info(f"Workflow {workflow_name} ist deaktiviert - überspringe")
                continue
                
            try:
                task_name = f'tasks.{workflow_name}.{self._get_task_function_name(workflow_name)}'
                
                if config['schedule'] == 'interval':
                    # Intervall-basierte Planung
                    self.scheduler.add_job(
                        func=self._execute_workflow,
                        trigger=IntervalTrigger(minutes=config['interval_minutes']),
                        args=[workflow_name, config['params']],
                        id=f'{workflow_name}_interval',
                        name=f'{workflow_name} (alle {config["interval_minutes"]} Min)',
                        max_instances=1,
                        coalesce=True,
                        misfire_grace_time=300
                    )
                    logger.info(f"Workflow {workflow_name} geplant - Intervall: {config['interval_minutes']} Min")
                    
                elif config['schedule'] == 'cron':
                    # Cron-basierte Planung
                    self.scheduler.add_job(
                        func=self._execute_workflow,
                        trigger=CronTrigger.from_crontab(config['cron']),
                        args=[workflow_name, config['params']],
                        id=f'{workflow_name}_cron',
                        name=f'{workflow_name} ({config["cron"]})',
                        max_instances=1,
                        coalesce=True,
                        misfire_grace_time=300
                    )
                    logger.info(f"Workflow {workflow_name} geplant - Cron: {config['cron']}")
                    
            except Exception as e:
                logger.error(f"Fehler beim Planen von Workflow {workflow_name}: {str(e)}")
    
    def _get_task_function_name(self, workflow_name):
        """Task-Funktionsname basierend auf Workflow-Name ermitteln"""
        task_mapping = {
            'google_maps_scraper': 'scrape_google_maps_leads',
            'linkedin_extractor': 'extract_linkedin_profiles',
            'ecommerce_intelligence': 'analyze_ecommerce_data',
            'social_media_harvester': 'harvest_social_media_data',
            'real_estate_analyzer': 'analyze_real_estate_market',
            'job_market_intelligence': 'analyze_job_market',
            'restaurant_analyzer': 'analyze_restaurant_data',
            'finance_data_collector': 'collect_finance_data',
            'event_scout': 'scout_events',
            'vehicle_market_intel': 'analyze_vehicle_market',
            'seo_opportunity_finder': 'find_seo_opportunities'
        }
        return task_mapping.get(workflow_name, 'unknown_task')
    
    def _execute_workflow(self, workflow_name, params):
        """Einzelnen Workflow ausführen"""
        try:
            task_function_name = self._get_task_function_name(workflow_name)
            task_name = f'tasks.{workflow_name}.{task_function_name}'
            
            # Task async starten
            result = celery_app.send_task(task_name, args=[params])
            
            # Status in Redis speichern
            status_key = f"workflow_status:{workflow_name}"
            self.redis_client.setex(
                status_key, 
                3600,  # 1 Stunde TTL
                f"started:{datetime.utcnow().isoformat()}:task_id:{result.id}"
            )
            
            logger.info(f"Workflow {workflow_name} gestartet - Task ID: {result.id}")
            
        except Exception as e:
            logger.error(f"Fehler beim Ausführen von Workflow {workflow_name}: {str(e)}")
            
            # Fehler in Redis loggen
            error_key = f"workflow_error:{workflow_name}"
            self.redis_client.setex(
                error_key,
                3600,
                f"error:{datetime.utcnow().isoformat()}:{str(e)}"
            )
    
    def schedule_system_maintenance(self):
        """System-Wartungsaufgaben planen"""
        # Health Checks alle 5 Minuten
        self.scheduler.add_job(
            func=self._execute_system_task,
            trigger=IntervalTrigger(minutes=5),
            args=['health_checks.check_all_services'],
            id='health_check_job',
            name='System Health Check',
            max_instances=1
        )
        
        # System-Metriken alle 15 Minuten
        self.scheduler.add_job(
            func=self._execute_system_task,
            trigger=IntervalTrigger(minutes=15),
            args=['health_checks.collect_system_metrics'],
            id='system_metrics_job',
            name='System Metrics Collection',
            max_instances=1
        )
        
        # Database-Cleanup täglich um 2:00 Uhr
        self.scheduler.add_job(
            func=self._execute_system_task,
            trigger=CronTrigger(hour=2, minute=0),
            args=['cleanup_jobs.cleanup_old_records'],
            id='cleanup_job',
            name='Database Cleanup',
            max_instances=1
        )
        
        # Failed Tasks Retry alle 30 Minuten
        self.scheduler.add_job(
            func=self._execute_system_task,
            trigger=IntervalTrigger(minutes=30),
            args=['cleanup_jobs.retry_failed_tasks'],
            id='retry_failed_job',
            name='Retry Failed Tasks',
            max_instances=1
        )
        
        # Performance-Monitoring alle 2 Stunden
        self.scheduler.add_job(
            func=self._execute_system_task,
            trigger=IntervalTrigger(hours=2),
            args=['health_checks.monitor_workflow_performance'],
            id='performance_monitoring_job',
            name='Workflow Performance Monitoring',
            max_instances=1
        )
        
        logger.info("System-Wartungsaufgaben geplant")
    
    def _execute_system_task(self, task_name):
        """System-Task ausführen"""
        try:
            full_task_name = f'tasks.{task_name}'
            result = celery_app.send_task(full_task_name)
            logger.info(f"System-Task {task_name} gestartet - Task ID: {result.id}")
        except Exception as e:
            logger.error(f"Fehler beim Ausführen von System-Task {task_name}: {str(e)}")
    
    def start(self):
        """Automation Manager starten"""
        logger.info("LeadMaps Automation Manager wird gestartet...")
        
        # Redis initialisieren
        if not self.initialize_redis():
            logger.error("Kann nicht ohne Redis starten - Beende...")
            sys.exit(1)
        
        try:
            # Workflows planen
            self.schedule_workflows()
            
            # System-Wartung planen
            self.schedule_system_maintenance()
            
            # Scheduler starten
            self.scheduler.start()
            self.running = True
            
            logger.info("Automation Manager erfolgreich gestartet")
            logger.info(f"Geplante Jobs: {len(self.scheduler.get_jobs())}")
            
            # Startup-Nachricht in Redis
            self.redis_client.setex(
                "automation_manager_status",
                86400,  # 24 Stunden
                f"running:{datetime.utcnow().isoformat()}:jobs:{len(self.scheduler.get_jobs())}"
            )
            
            # Haupt-Loop für kontinuierliches Monitoring
            self._main_loop()
            
        except Exception as e:
            logger.error(f"Fehler beim Starten des Automation Managers: {str(e)}")
            self.stop()
            sys.exit(1)
    
    def _main_loop(self):
        """Haupt-Monitoring-Loop"""
        while self.running:
            try:
                # Status-Check alle 60 Sekunden
                time.sleep(60)
                
                # Lebenszeichen in Redis
                self.redis_client.setex(
                    "automation_manager_heartbeat",
                    300,  # 5 Minuten TTL
                    datetime.utcnow().isoformat()
                )
                
                # Scheduler-Status prüfen
                if not self.scheduler.running:
                    logger.warning("Scheduler ist nicht mehr aktiv - Neustart...")
                    self.scheduler.start()
                
                # Job-Status loggen (alle 10 Minuten)
                if datetime.utcnow().minute % 10 == 0:
                    active_jobs = len(self.scheduler.get_jobs())
                    logger.info(f"Status-Check: {active_jobs} aktive Jobs, Scheduler läuft: {self.scheduler.running}")
                
            except KeyboardInterrupt:
                logger.info("Keyboard Interrupt empfangen - Stoppe...")
                break
            except Exception as e:
                logger.error(f"Fehler in Haupt-Loop: {str(e)}")
                time.sleep(30)  # Kurze Pause vor Fortsetzung
    
    def stop(self):
        """Automation Manager stoppen"""
        logger.info("Automation Manager wird gestoppt...")
        
        self.running = False
        
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("Scheduler gestoppt")
        
        # Status in Redis aktualisieren
        if self.redis_client:
            self.redis_client.setex(
                "automation_manager_status",
                300,
                f"stopped:{datetime.utcnow().isoformat()}"
            )
        
        logger.info("Automation Manager erfolgreich gestoppt")

def main():
    """Hauptfunktion"""
    print("🚀 LeadMaps Automation Manager")
    print("=" * 50)
    print("Starte autonomes Multi-Workflow-System...")
    
    manager = AutomationManager()
    
    try:
        manager.start()
    except KeyboardInterrupt:
        print("\n⚠️  Shutdown durch Benutzer initiiert")
    except Exception as e:
        print(f"❌ Kritischer Fehler: {str(e)}")
        sys.exit(1)
    finally:
        manager.stop()
        print("✅ Automation Manager beendet")

if __name__ == "__main__":
    main()