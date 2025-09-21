from celery_app import celery_app
from tasks.base_scraper import BaseScraper
import asyncio
import logging
from datetime import datetime

# Import aller Workflow-Tasks
from tasks.linkedin_extractor import extract_linkedin_profiles
from tasks.ecommerce_intelligence import analyze_ecommerce_data
from tasks.social_media_harvester import harvest_social_media_data
from tasks.real_estate_analyzer import analyze_real_estate_market
from tasks.job_market_intelligence import analyze_job_market
from tasks.restaurant_analyzer import analyze_restaurant_data
from tasks.finance_data_collector import collect_finance_data
from tasks.event_scout import scout_events
from tasks.vehicle_market_intel import analyze_vehicle_market
from tasks.seo_opportunity_finder import find_seo_opportunities

logger = logging.getLogger(__name__)

class WorkflowManager(BaseScraper):
    """Manager für alle Workflow-Automatisierungen"""
    pass

@celery_app.task(bind=True, base=WorkflowManager)
def execute_multi_workflow(self, workflow_configs):
    """Führe mehrere Workflows parallel aus"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        task_id = loop.run_until_complete(
            self.log_task_start("multi_workflow", workflow_configs)
        )
        
        # Workflow-Mapping
        workflow_tasks = {
            'linkedin_extractor': extract_linkedin_profiles,
            'ecommerce_intelligence': analyze_ecommerce_data,
            'social_media_harvester': harvest_social_media_data,
            'real_estate_analyzer': analyze_real_estate_market,
            'job_market_intelligence': analyze_job_market,
            'restaurant_analyzer': analyze_restaurant_data,
            'finance_data_collector': collect_finance_data,
            'event_scout': scout_events,
            'vehicle_market_intel': analyze_vehicle_market,
            'seo_opportunity_finder': find_seo_opportunities
        }
        
        results = {}
        
        # Workflows parallel starten
        for workflow_name, config in workflow_configs.items():
            if workflow_name in workflow_tasks:
                logger.info(f"Starte Workflow: {workflow_name}")
                
                # Task async starten
                task_func = workflow_tasks[workflow_name]
                result = task_func.apply_async(args=[config])
                
                # Ergebnis sammeln
                try:
                    workflow_result = result.get(timeout=600)  # 10 Minuten Timeout
                    results[workflow_name] = workflow_result
                    logger.info(f"Workflow {workflow_name} erfolgreich abgeschlossen")
                except Exception as e:
                    logger.error(f"Workflow {workflow_name} fehlgeschlagen: {str(e)}")
                    results[workflow_name] = {'success': False, 'error': str(e)}
        
        # Gesamtergebnis loggen
        success_count = sum(1 for r in results.values() if r.get('success', False))
        total_count = len(results)
        
        loop.run_until_complete(
            self.log_task_completion(task_id, list(results.values()), success=success_count > 0)
        )
        
        logger.info(f"Multi-Workflow abgeschlossen: {success_count}/{total_count} erfolgreich")
        
        return {
            'success': success_count > 0,
            'task_id': task_id,
            'workflows_executed': total_count,
            'workflows_successful': success_count,
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Multi-Workflow fehlgeschlagen: {str(e)}")
        raise self.retry(exc=e, countdown=180, max_retries=2)

@celery_app.task(bind=True, base=WorkflowManager)
def schedule_recurring_workflows(self, schedule_config):
    """Plant wiederkehrende Workflow-Ausführungen"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        task_id = loop.run_until_complete(
            self.log_task_start("recurring_workflows", schedule_config)
        )
        
        # Für jeden konfigurierten Workflow
        scheduled_tasks = []
        
        for workflow_name, config in schedule_config.items():
            # Nächste Ausführungszeit berechnen
            next_run = datetime.utcnow()
            
            # Task für zukünftige Ausführung planen
            task_result = execute_multi_workflow.apply_async(
                args=[{workflow_name: config['params']}],
                eta=next_run
            )
            
            scheduled_tasks.append({
                'workflow': workflow_name,
                'task_id': task_result.id,
                'scheduled_for': next_run.isoformat()
            })
        
        loop.run_until_complete(
            self.log_task_completion(task_id, scheduled_tasks, success=True)
        )
        
        logger.info(f"Wiederkehrende Workflows geplant: {len(scheduled_tasks)}")
        
        return {
            'success': True,
            'task_id': task_id,
            'scheduled_workflows': len(scheduled_tasks),
            'tasks': scheduled_tasks
        }
        
    except Exception as e:
        logger.error(f"Workflow-Planung fehlgeschlagen: {str(e)}")
        raise self.retry(exc=e, countdown=60, max_retries=2)

@celery_app.task(bind=True, base=WorkflowManager)
def auto_workflow_optimizer(self):
    """Automatische Optimierung der Workflow-Performance"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        task_id = loop.run_until_complete(
            self.log_task_start("workflow_optimizer", {})
        )
        
        # Performance-Metriken sammeln
        from database import db
        
        # Letzte 24 Stunden analysieren  
        recent_tasks_cursor = db.automation_tasks.find({
            'started_at': {'$gte': datetime.utcnow().replace(hour=0, minute=0, second=0)}
        })
        recent_tasks = loop.run_until_complete(recent_tasks_cursor.to_list(1000))
        
        # Performance-Statistiken
        stats = {}
        
        for task in recent_tasks:
            workflow_type = task.get('workflow_type', 'unknown')
            
            if workflow_type not in stats:
                stats[workflow_type] = {
                    'total_runs': 0,
                    'successful_runs': 0,
                    'failed_runs': 0,
                    'avg_duration': 0,
                    'total_results': 0
                }
            
            stats[workflow_type]['total_runs'] += 1
            
            if task.get('status') == 'completed':
                stats[workflow_type]['successful_runs'] += 1
                stats[workflow_type]['total_results'] += task.get('results_count', 0)
            else:
                stats[workflow_type]['failed_runs'] += 1
        
        # Optimierungsempfehlungen generieren
        optimizations = []
        
        for workflow_type, stat in stats.items():
            success_rate = stat['successful_runs'] / stat['total_runs'] if stat['total_runs'] > 0 else 0
            
            if success_rate < 0.8:  # Unter 80% Erfolgsrate
                optimizations.append({
                    'workflow': workflow_type,
                    'issue': 'low_success_rate',
                    'current_rate': success_rate,
                    'recommendation': 'Erhöhe Retry-Limits und reduziere Rate-Limiting'
                })
            
            if stat['total_results'] / stat['successful_runs'] < 5 if stat['successful_runs'] > 0 else False:
                optimizations.append({
                    'workflow': workflow_type,
                    'issue': 'low_yield',
                    'recommendation': 'Erweitere Suchparameter und Datenquellen'
                })
        
        loop.run_until_complete(
            self.log_task_completion(task_id, optimizations, success=True)
        )
        
        logger.info(f"Workflow-Optimierung abgeschlossen: {len(optimizations)} Empfehlungen")
        
        return {
            'success': True,
            'task_id': task_id,
            'statistics': stats,
            'optimizations': optimizations
        }
        
    except Exception as e:
        logger.error(f"Workflow-Optimierung fehlgeschlagen: {str(e)}")
        raise self.retry(exc=e, countdown=300, max_retries=1)