from celery_app import celery_app
from tasks.base_scraper import BaseScraper
import asyncio
import logging
from datetime import datetime, timedelta
from database import db

logger = logging.getLogger(__name__)

class CleanupManager(BaseScraper):
    """Database Cleanup Manager Task"""
    pass

@celery_app.task(bind=True, base=CleanupManager)
def cleanup_old_records(self):
    """Alte Datensätze bereinigen"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        task_id = loop.run_until_complete(
            self.log_task_start("cleanup_old_records", {})
        )
        
        cleanup_results = {}
        
        # Datum für Cleanup (30 Tage alt)
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        # Collections für Cleanup
        collections_to_clean = [
            'automation_tasks',
            'health_checks', 
            'system_metrics',
            'performance_reports',
            'google_maps_results',
            'linkedin_profiles_results',
            'ecommerce_products_results',
            'social_media_accounts_results',
            'real_estate_properties_results',
            'job_market_positions_results',
            'restaurants_results',
            'financial_instruments_results',
            'events_results',
            'vehicles_results',
            'seo_opportunities_results'
        ]
        
        total_deleted = 0
        
        for collection_name in collections_to_clean:
            try:
                collection = getattr(db, collection_name)
                
                # Anzahl alter Records zählen
                old_count = loop.run_until_complete(
                    collection.count_documents({'created_at': {'$lt': cutoff_date}})
                )
                
                if old_count > 0:
                    # Alte Records löschen
                    delete_result = loop.run_until_complete(
                        collection.delete_many({'created_at': {'$lt': cutoff_date}})
                    )
                    
                    cleanup_results[collection_name] = {
                        'deleted_count': delete_result.deleted_count,
                        'status': 'cleaned'
                    }
                    
                    total_deleted += delete_result.deleted_count
                    logger.info(f"Collection {collection_name}: {delete_result.deleted_count} Records gelöscht")
                else:
                    cleanup_results[collection_name] = {
                        'deleted_count': 0,
                        'status': 'no_old_records'
                    }
                    
            except Exception as e:
                cleanup_results[collection_name] = {
                    'deleted_count': 0,
                    'status': 'error',
                    'error': str(e)
                }
                logger.error(f"Cleanup-Fehler für {collection_name}: {str(e)}")
        
        # Cleanup-Report erstellen
        cleanup_report = {
            'timestamp': datetime.utcnow(),
            'cutoff_date': cutoff_date,
            'total_deleted_records': total_deleted,
            'collections': cleanup_results
        }
        
        loop.run_until_complete(
            self.log_task_completion(task_id, [cleanup_report], success=True)
        )
        
        logger.info(f"Database-Cleanup abgeschlossen - {total_deleted} Records gelöscht")
        
        return cleanup_report
        
    except Exception as e:
        logger.error(f"Database-Cleanup fehlgeschlagen: {str(e)}")
        raise self.retry(exc=e, countdown=300, max_retries=1)

@celery_app.task(bind=True, base=CleanupManager) 
def retry_failed_tasks(self):
    """Fehlgeschlagene Tasks erneut versuchen"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        task_id = loop.run_until_complete(
            self.log_task_start("retry_failed_tasks", {})
        )
        
        # Fehlgeschlagene Tasks der letzten 6 Stunden finden
        retry_cutoff = datetime.utcnow() - timedelta(hours=6)
        
        failed_tasks_cursor = db.automation_tasks.find({
            'status': 'failed',
            'started_at': {'$gte': retry_cutoff},
            'retry_count': {'$lt': 3}  # Maximal 3 Retry-Versuche
        })
        failed_tasks = loop.run_until_complete(failed_tasks_cursor.to_list(100))
        
        retry_results = {
            'retried_tasks': 0,
            'successful_retries': 0,
            'failed_retries': 0,
            'task_details': []
        }
        
        # Task-Mapping für Retry
        task_mapping = {
            'google_maps_scraper': 'tasks.google_maps_scraper.scrape_google_maps_leads',
            'linkedin_extractor': 'tasks.linkedin_extractor.extract_linkedin_profiles',
            'ecommerce_intelligence': 'tasks.ecommerce_intelligence.analyze_ecommerce_data',
            'social_media_harvester': 'tasks.social_media_harvester.harvest_social_media_data',
            'real_estate_analyzer': 'tasks.real_estate_analyzer.analyze_real_estate_market',
            'job_market_intelligence': 'tasks.job_market_intelligence.analyze_job_market',
            'restaurant_analyzer': 'tasks.restaurant_analyzer.analyze_restaurant_data',
            'finance_data_collector': 'tasks.finance_data_collector.collect_finance_data',
            'event_scout': 'tasks.event_scout.scout_events',
            'vehicle_market_intel': 'tasks.vehicle_market_intel.analyze_vehicle_market',
            'seo_opportunity_finder': 'tasks.seo_opportunity_finder.find_seo_opportunities'
        }
        
        for failed_task in failed_tasks:
            workflow_type = failed_task.get('workflow_type')
            
            if workflow_type in task_mapping:
                try:
                    # Retry-Count erhöhen
                    current_retry = failed_task.get('retry_count', 0) + 1
                    
                    loop.run_until_complete(
                        db.automation_tasks.update_one(
                            {'id': failed_task['id']},
                            {'$set': {'retry_count': current_retry, 'status': 'retrying'}}
                        )
                    )
                    
                    # Task erneut starten (delayed)
                    from celery_app import celery_app
                    celery_app.send_task(
                        task_mapping[workflow_type],
                        args=[failed_task.get('parameters', {})],
                        countdown=300  # 5 Minuten Verzögerung
                    )
                    
                    retry_results['retried_tasks'] += 1
                    retry_results['task_details'].append({
                        'task_id': failed_task['id'],
                        'workflow_type': workflow_type,
                        'retry_attempt': current_retry,
                        'status': 'scheduled_for_retry'
                    })
                    
                    logger.info(f"Task {failed_task['id']} ({workflow_type}) für Retry geplant")
                    
                except Exception as e:
                    retry_results['failed_retries'] += 1
                    retry_results['task_details'].append({
                        'task_id': failed_task['id'], 
                        'workflow_type': workflow_type,
                        'status': 'retry_failed',
                        'error': str(e)
                    })
                    
                    logger.error(f"Retry für Task {failed_task['id']} fehlgeschlagen: {str(e)}")
        
        loop.run_until_complete(
            self.log_task_completion(task_id, [retry_results], success=True)
        )
        
        logger.info(f"Task-Retry abgeschlossen - {retry_results['retried_tasks']} Tasks für Wiederholung geplant")
        
        return retry_results
        
    except Exception as e:
        logger.error(f"Task-Retry fehlgeschlagen: {str(e)}")
        raise self.retry(exc=e, countdown=600, max_retries=1)

@celery_app.task(bind=True, base=CleanupManager)
def optimize_database_indexes(self):
    """Database-Indizes optimieren"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        task_id = loop.run_until_complete(
            self.log_task_start("optimize_db_indexes", {})
        )
        
        # Wichtige Indizes erstellen/optimieren
        index_operations = []
        
        # Automation Tasks Indizes
        try:
            loop.run_until_complete(
                db.automation_tasks.create_index([("workflow_type", 1), ("status", 1)])
            )
            loop.run_until_complete(
                db.automation_tasks.create_index([("started_at", -1)])
            )
            index_operations.append({"collection": "automation_tasks", "status": "success"})
        except Exception as e:
            index_operations.append({"collection": "automation_tasks", "status": "error", "error": str(e)})
        
        # Health Checks Indizes
        try:
            loop.run_until_complete(
                db.health_checks.create_index([("timestamp", -1)])
            )
            index_operations.append({"collection": "health_checks", "status": "success"})
        except Exception as e:
            index_operations.append({"collection": "health_checks", "status": "error", "error": str(e)})
        
        # System Metrics Indizes
        try:
            loop.run_until_complete(
                db.system_metrics.create_index([("timestamp", -1)])
            )
            index_operations.append({"collection": "system_metrics", "status": "success"})
        except Exception as e:
            index_operations.append({"collection": "system_metrics", "status": "error", "error": str(e)})
        
        # Alle Results Collections
        result_collections = [
            'google_maps_results', 'linkedin_profiles_results', 'ecommerce_products_results',
            'social_media_accounts_results', 'real_estate_properties_results', 
            'job_market_positions_results', 'restaurants_results', 'financial_instruments_results',
            'events_results', 'vehicles_results', 'seo_opportunities_results'
        ]
        
        for collection_name in result_collections:
            try:
                collection = getattr(db, collection_name)
                loop.run_until_complete(
                    collection.create_index([("task_id", 1), ("created_at", -1)])
                )
                index_operations.append({"collection": collection_name, "status": "success"})
            except Exception as e:
                index_operations.append({"collection": collection_name, "status": "error", "error": str(e)})
        
        optimization_report = {
            'timestamp': datetime.utcnow(),
            'total_collections': len(index_operations),
            'successful_operations': len([op for op in index_operations if op['status'] == 'success']),
            'failed_operations': len([op for op in index_operations if op['status'] == 'error']),
            'operations': index_operations
        }
        
        loop.run_until_complete(
            self.log_task_completion(task_id, [optimization_report], success=True)
        )
        
        logger.info(f"Database-Index-Optimierung abgeschlossen - {optimization_report['successful_operations']}/{optimization_report['total_collections']} erfolgreich")
        
        return optimization_report
        
    except Exception as e:
        logger.error(f"Database-Index-Optimierung fehlgeschlagen: {str(e)}")
        raise self.retry(exc=e, countdown=600, max_retries=1)