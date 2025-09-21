from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any
import asyncio
import uuid
from datetime import datetime, timedelta
from database import db
from pydantic import BaseModel

router = APIRouter(prefix="/api/automation", tags=["automation"])

class WorkflowStatus(BaseModel):
    workflow_name: str
    status: str
    last_run: str
    next_run: str
    success_rate: float
    total_runs: int

class SystemHealth(BaseModel):
    overall_status: str
    services: Dict[str, Any]
    system_resources: Dict[str, Any]
    timestamp: str

@router.get("/dashboard/overview")
async def get_automation_overview():
    """Automation Dashboard Übersicht"""
    try:
        # Aktuelle Zeit
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        
        # Tasks der letzten 24 Stunden
        recent_tasks_cursor = db.automation_tasks.find({
            'started_at': {'$gte': last_24h}
        })
        recent_tasks = await recent_tasks_cursor.to_list(1000)
        
        # Workflow-Statistiken
        workflow_stats = {}
        total_workflows = 11  # Anzahl verfügbare Workflows
        
        for task in recent_tasks:
            workflow_type = task.get('workflow_type', 'unknown')
            
            if workflow_type not in workflow_stats:
                workflow_stats[workflow_type] = {
                    'total_runs': 0,
                    'successful_runs': 0,
                    'failed_runs': 0,
                    'total_results': 0,
                    'last_run': None,
                    'status': 'idle'
                }
            
            workflow_stats[workflow_type]['total_runs'] += 1
            
            if task.get('status') == 'completed':
                workflow_stats[workflow_type]['successful_runs'] += 1
                workflow_stats[workflow_type]['total_results'] += task.get('results_count', 0)
            elif task.get('status') == 'failed':
                workflow_stats[workflow_type]['failed_runs'] += 1
            elif task.get('status') == 'running':
                workflow_stats[workflow_type]['status'] = 'running'
            
            # Letzte Ausführung
            if not workflow_stats[workflow_type]['last_run'] or task.get('started_at') > workflow_stats[workflow_type]['last_run']:
                workflow_stats[workflow_type]['last_run'] = task.get('started_at')
        
        # Erfolgsraten berechnen
        for workflow_type, stats in workflow_stats.items():
            if stats['total_runs'] > 0:
                stats['success_rate'] = stats['successful_runs'] / stats['total_runs']
            else:
                stats['success_rate'] = 0.0
        
        # Aktuelle System-Health
        health_cursor = db.health_checks.find().sort('timestamp', -1).limit(1)
        health_records = await health_cursor.to_list(1)
        current_health = health_records[0] if health_records else None
        
        # Übersicht zusammenstellen
        overview = {
            'timestamp': now.isoformat(),
            'automation_status': 'running',
            'total_workflows': total_workflows,
            'active_workflows': len([w for w in workflow_stats.values() if w['status'] == 'running']),
            'successful_workflows': len([w for w in workflow_stats.values() if w['success_rate'] > 0.8]),
            'total_tasks_24h': len(recent_tasks),
            'successful_tasks_24h': len([t for t in recent_tasks if t.get('status') == 'completed']),
            'failed_tasks_24h': len([t for t in recent_tasks if t.get('status') == 'failed']),
            'total_results_24h': sum(t.get('results_count', 0) for t in recent_tasks),
            'system_health': current_health.get('overall_status', 'unknown') if current_health else 'unknown',
            'workflow_statistics': workflow_stats
        }
        
        return overview
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Übersicht: {str(e)}")

@router.get("/workflows/status")
async def get_all_workflow_status():
    """Status aller Workflows abrufen"""
    try:
        workflows = [
            'google_maps_scraper', 'linkedin_extractor', 'ecommerce_intelligence',
            'social_media_harvester', 'real_estate_analyzer', 'job_market_intelligence',
            'restaurant_analyzer', 'finance_data_collector', 'event_scout',
            'vehicle_market_intel', 'seo_opportunity_finder'
        ]
        
        workflow_statuses = []
        
        for workflow_name in workflows:
            # Letzte Ausführungen finden
            recent_cursor = db.automation_tasks.find({
                'workflow_type': workflow_name
            }).sort('started_at', -1).limit(10)
            recent_tasks = await recent_cursor.to_list(10)
            
            if recent_tasks:
                last_task = recent_tasks[0]
                success_count = len([t for t in recent_tasks if t.get('status') == 'completed'])
                success_rate = success_count / len(recent_tasks) if recent_tasks else 0
                
                status = WorkflowStatus(
                    workflow_name=workflow_name,
                    status=last_task.get('status', 'unknown'),
                    last_run=last_task.get('started_at', datetime.min).isoformat(),
                    next_run=(datetime.utcnow() + timedelta(hours=1)).isoformat(),  # Geschätzt
                    success_rate=success_rate,
                    total_runs=len(recent_tasks)
                )
            else:
                status = WorkflowStatus(
                    workflow_name=workflow_name,
                    status='never_run',
                    last_run='never',
                    next_run='scheduled',
                    success_rate=0.0,
                    total_runs=0
                )
            
            workflow_statuses.append(status)
        
        return workflow_statuses
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Workflow-Status: {str(e)}")

@router.get("/system/health")
async def get_system_health():
    """Aktuelle System-Health abrufen"""
    try:
        # Neueste Health-Checks
        health_cursor = db.health_checks.find().sort('timestamp', -1).limit(1)
        health_records = await health_cursor.to_list(1)
        
        if not health_records:
            return SystemHealth(
                overall_status='unknown',
                services={},
                system_resources={},
                timestamp=datetime.utcnow().isoformat()
            )
        
        health_data = health_records[0]
        
        return SystemHealth(
            overall_status=health_data.get('overall_status', 'unknown'),
            services=health_data.get('services', {}),
            system_resources=health_data.get('system_resources', {}),
            timestamp=health_data.get('timestamp', datetime.utcnow().isoformat())
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der System-Health: {str(e)}")

@router.get("/metrics/performance")
async def get_performance_metrics():
    """Performance-Metriken der letzten Zeit"""
    try:
        # System-Metriken der letzten 6 Stunden
        since = datetime.utcnow() - timedelta(hours=6)
        
        metrics_cursor = db.system_metrics.find({
            'timestamp': {'$gte': since}
        }).sort('timestamp', -1)
        metrics = await metrics_cursor.to_list(100)
        
        # Performance-Reports
        reports_cursor = db.performance_reports.find().sort('timestamp', -1).limit(5)
        reports = await reports_cursor.to_list(5)
        
        return {
            'system_metrics': metrics,
            'performance_reports': reports,
            'metrics_count': len(metrics),
            'reports_count': len(reports)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Metriken: {str(e)}")

@router.post("/workflows/{workflow_name}/trigger")
async def trigger_workflow_manually(workflow_name: str, params: Dict[str, Any] = None):
    """Workflow manuell auslösen (vereinfacht ohne Celery)"""
    try:
        # Verfügbare Workflows prüfen
        available_workflows = [
            'google_maps_scraper', 'linkedin_extractor', 'ecommerce_intelligence',
            'social_media_harvester', 'real_estate_analyzer', 'job_market_intelligence',
            'restaurant_analyzer', 'finance_data_collector', 'event_scout',
            'vehicle_market_intel', 'seo_opportunity_finder'
        ]
        
        if workflow_name not in available_workflows:
            raise HTTPException(status_code=404, detail=f"Workflow '{workflow_name}' nicht gefunden")
        
        # Default-Parameter falls keine angegeben
        if not params:
            params = {'max_results': 20, 'triggered_manually': True}
        
        # Task-Record erstellen (ohne Celery)
        task_record = {
            'id': str(uuid.uuid4()),
            'workflow_type': workflow_name,
            'status': 'scheduled',
            'parameters': params,
            'started_at': datetime.utcnow(),
            'triggered_manually': True
        }
        
        await db.automation_tasks.insert_one(task_record)
        
        return {
            'success': True,
            'workflow_name': workflow_name,
            'task_id': task_record['id'],
            'message': f"Workflow '{workflow_name}' wurde zur Ausführung geplant",
            'parameters': params,
            'note': 'Task wird vom Simple Scheduler in der nächsten Ausführung verarbeitet'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Planen des Workflows: {str(e)}")

@router.get("/tasks/recent")
async def get_recent_tasks(limit: int = 50):
    """Aktuelle Tasks abrufen"""
    try:
        tasks_cursor = db.automation_tasks.find().sort('started_at', -1).limit(limit)
        tasks = await tasks_cursor.to_list(limit)
        
        # Für Frontend formatieren
        formatted_tasks = []
        for task in tasks:
            formatted_task = {
                'id': task.get('id'),
                'workflow_type': task.get('workflow_type'),
                'status': task.get('status'),
                'started_at': task.get('started_at', datetime.min).isoformat(),
                'completed_at': task.get('completed_at', '').isoformat() if task.get('completed_at') else None,
                'results_count': task.get('results_count', 0),
                'parameters': task.get('parameters', {})
            }
            formatted_tasks.append(formatted_task)
        
        return {
            'tasks': formatted_tasks,
            'total_count': len(formatted_tasks)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Tasks: {str(e)}")

@router.get("/statistics/summary")
async def get_automation_statistics():
    """Zusammenfassende Statistiken"""
    try:
        now = datetime.utcnow()
        
        # Verschiedene Zeiträume
        periods = {
            'last_hour': now - timedelta(hours=1),
            'last_24h': now - timedelta(hours=24),
            'last_week': now - timedelta(days=7),
            'last_month': now - timedelta(days=30)
        }
        
        stats = {}
        
        for period_name, start_time in periods.items():
            tasks_cursor = db.automation_tasks.find({
                'started_at': {'$gte': start_time}
            })
            tasks = await tasks_cursor.to_list(10000)
            
            stats[period_name] = {
                'total_tasks': len(tasks),
                'successful_tasks': len([t for t in tasks if t.get('status') == 'completed']),
                'failed_tasks': len([t for t in tasks if t.get('status') == 'failed']),
                'running_tasks': len([t for t in tasks if t.get('status') == 'running']),
                'total_results': sum(t.get('results_count', 0) for t in tasks)
            }
            
            # Erfolgsrate berechnen
            if stats[period_name]['total_tasks'] > 0:
                stats[period_name]['success_rate'] = stats[period_name]['successful_tasks'] / stats[period_name]['total_tasks']
            else:
                stats[period_name]['success_rate'] = 0.0
        
        return {
            'generated_at': now.isoformat(),
            'periods': stats,
            'automation_uptime': '24/7',
            'total_workflows': 11
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Erstellen der Statistiken: {str(e)}")