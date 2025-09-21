from celery_app import celery_app
from tasks.base_scraper import BaseScraper
import asyncio
import logging
import psutil
import time
from datetime import datetime
import redis
from database import db, client as mongo_client

logger = logging.getLogger(__name__)

class HealthChecker(BaseScraper):
    """System Health Checker Task"""
    pass

@celery_app.task(bind=True, base=HealthChecker)
def check_all_services(self):
    """Umfassender Service-Health-Check"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        task_id = loop.run_until_complete(
            self.log_task_start("health_check_all", {})
        )
        
        health_status = {
            'timestamp': datetime.utcnow().isoformat(),
            'overall_status': 'healthy',
            'services': {}
        }
        
        # MongoDB Health Check
        try:
            start_time = time.time()
            loop.run_until_complete(db.health_checks.insert_one({'test': True, 'timestamp': datetime.utcnow()}))
            mongo_response_time = (time.time() - start_time) * 1000
            
            health_status['services']['mongodb'] = {
                'status': 'healthy',
                'response_time_ms': round(mongo_response_time, 2),
                'connection': 'active'
            }
            
        except Exception as e:
            health_status['services']['mongodb'] = {
                'status': 'unhealthy',
                'error': str(e),
                'connection': 'failed'
            }
            health_status['overall_status'] = 'degraded'
        
        # Redis Health Check
        try:
            redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            start_time = time.time()
            redis_client.ping()
            redis_response_time = (time.time() - start_time) * 1000
            
            health_status['services']['redis'] = {
                'status': 'healthy',
                'response_time_ms': round(redis_response_time, 2),
                'connection': 'active'
            }
            
        except Exception as e:
            health_status['services']['redis'] = {
                'status': 'unhealthy',
                'error': str(e),
                'connection': 'failed'
            }
            health_status['overall_status'] = 'degraded'
        
        # Celery Worker Health Check
        try:
            from celery_app import celery_app
            inspect = celery_app.control.inspect()
            
            # Aktive Workers prüfen
            active_workers = inspect.active()
            registered_tasks = inspect.registered()
            
            worker_count = len(active_workers) if active_workers else 0
            
            health_status['services']['celery'] = {
                'status': 'healthy' if worker_count > 0 else 'unhealthy',
                'active_workers': worker_count,
                'registered_tasks_count': len(registered_tasks) if registered_tasks else 0
            }
            
            if worker_count == 0:
                health_status['overall_status'] = 'degraded'
                
        except Exception as e:
            health_status['services']['celery'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            health_status['overall_status'] = 'degraded'
        
        # System Resources Check
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        disk_percent = psutil.disk_usage('/').percent
        
        health_status['system_resources'] = {
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'disk_percent': disk_percent,
            'status': 'healthy' if all([cpu_percent < 90, memory_percent < 90, disk_percent < 90]) else 'warning'
        }
        
        if health_status['system_resources']['status'] == 'warning':
            health_status['overall_status'] = 'degraded'
        
        # Health Check in DB speichern
        loop.run_until_complete(
            db.health_checks.insert_one(health_status)
        )
        
        loop.run_until_complete(
            self.log_task_completion(task_id, [health_status], success=True)
        )
        
        logger.info(f"Health Check abgeschlossen - Status: {health_status['overall_status']}")
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health Check fehlgeschlagen: {str(e)}")
        raise self.retry(exc=e, countdown=60, max_retries=2)

@celery_app.task(bind=True, base=HealthChecker)
def collect_system_metrics(self):
    """System-Metriken sammeln"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        task_id = loop.run_until_complete(
            self.log_task_start("system_metrics", {})
        )
        
        # System-Metriken sammeln
        metrics = {
            'timestamp': datetime.utcnow(),
            'cpu': {
                'percent': psutil.cpu_percent(interval=1),
                'count': psutil.cpu_count(),
                'frequency': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            },
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent,
                'used': psutil.virtual_memory().used
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'free': psutil.disk_usage('/').free,
                'percent': psutil.disk_usage('/').percent
            },
            'network': {
                'bytes_sent': psutil.net_io_counters().bytes_sent,
                'bytes_recv': psutil.net_io_counters().bytes_recv,
                'packets_sent': psutil.net_io_counters().packets_sent,
                'packets_recv': psutil.net_io_counters().packets_recv
            }
        }
        
        # Task-Performance-Metriken
        recent_tasks_cursor = db.automation_tasks.find({
            'started_at': {'$gte': datetime.utcnow().replace(minute=0, second=0, microsecond=0)}
        })
        recent_tasks = loop.run_until_complete(recent_tasks_cursor.to_list(1000))
        
        task_metrics = {
            'total_tasks_this_hour': len(recent_tasks),
            'successful_tasks': len([t for t in recent_tasks if t.get('status') == 'completed']),
            'failed_tasks': len([t for t in recent_tasks if t.get('status') == 'failed']),
            'running_tasks': len([t for t in recent_tasks if t.get('status') == 'running'])
        }
        
        metrics['tasks'] = task_metrics
        
        # Metriken in DB speichern
        loop.run_until_complete(
            db.system_metrics.insert_one(metrics)
        )
        
        loop.run_until_complete(
            self.log_task_completion(task_id, [metrics], success=True)
        )
        
        logger.info(f"System-Metriken gesammelt - CPU: {metrics['cpu']['percent']}%, Memory: {metrics['memory']['percent']}%")
        
        return metrics
        
    except Exception as e:
        logger.error(f"Metriken-Sammlung fehlgeschlagen: {str(e)}")
        raise self.retry(exc=e, countdown=120, max_retries=2)

@celery_app.task(bind=True, base=HealthChecker)
def monitor_workflow_performance(self):
    """Workflow-Performance überwachen"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        task_id = loop.run_until_complete(
            self.log_task_start("workflow_performance", {})
        )
        
        # Performance-Daten der letzten 24 Stunden
        yesterday = datetime.utcnow().replace(hour=0, minute=0, second=0)
        
        performance_cursor = db.automation_tasks.find({
            'started_at': {'$gte': yesterday}
        })
        tasks_24h = loop.run_until_complete(performance_cursor.to_list(10000))
        
        # Workflow-spezifische Analyse
        workflow_stats = {}
        
        for task in tasks_24h:
            workflow_type = task.get('workflow_type', 'unknown')
            
            if workflow_type not in workflow_stats:
                workflow_stats[workflow_type] = {
                    'total_runs': 0,
                    'successful_runs': 0,
                    'failed_runs': 0,
                    'total_results': 0,
                    'avg_duration_seconds': 0,
                    'success_rate': 0
                }
            
            workflow_stats[workflow_type]['total_runs'] += 1
            
            if task.get('status') == 'completed':
                workflow_stats[workflow_type]['successful_runs'] += 1
                workflow_stats[workflow_type]['total_results'] += task.get('results_count', 0)
                
                # Durchschnittliche Dauer berechnen
                if task.get('started_at') and task.get('completed_at'):
                    duration = (task['completed_at'] - task['started_at']).total_seconds()
                    workflow_stats[workflow_type]['avg_duration_seconds'] += duration
            else:
                workflow_stats[workflow_type]['failed_runs'] += 1
        
        # Erfolgsraten berechnen
        for workflow_type, stats in workflow_stats.items():
            if stats['total_runs'] > 0:
                stats['success_rate'] = stats['successful_runs'] / stats['total_runs']
                
                if stats['successful_runs'] > 0:
                    stats['avg_duration_seconds'] = stats['avg_duration_seconds'] / stats['successful_runs']
        
        performance_report = {
            'timestamp': datetime.utcnow(),
            'analysis_period': '24_hours',
            'total_tasks': len(tasks_24h),
            'workflows': workflow_stats,
            'alerts': []
        }
        
        # Performance-Alerts generieren
        for workflow_type, stats in workflow_stats.items():
            if stats['success_rate'] < 0.8:  # Unter 80% Erfolgsrate
                performance_report['alerts'].append({
                    'type': 'low_success_rate',
                    'workflow': workflow_type,
                    'current_rate': stats['success_rate'],
                    'threshold': 0.8,
                    'severity': 'warning'
                })
            
            if stats['avg_duration_seconds'] > 300:  # Über 5 Minuten
                performance_report['alerts'].append({
                    'type': 'slow_performance',
                    'workflow': workflow_type,
                    'current_duration': stats['avg_duration_seconds'],
                    'threshold': 300,
                    'severity': 'warning'
                })
        
        # Performance-Report in DB speichern
        loop.run_until_complete(
            db.performance_reports.insert_one(performance_report)
        )
        
        loop.run_until_complete(
            self.log_task_completion(task_id, [performance_report], success=True)
        )
        
        alert_count = len(performance_report['alerts'])
        logger.info(f"Workflow-Performance überwacht - {alert_count} Alerts generiert")
        
        return performance_report
        
    except Exception as e:
        logger.error(f"Performance-Monitoring fehlgeschlagen: {str(e)}")
        raise self.retry(exc=e, countdown=180, max_retries=2)