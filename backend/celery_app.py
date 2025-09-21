from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

# Redis als Broker und Backend
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Celery App konfigurieren
celery_app = Celery(
    'leadmaps_automation',
    broker=redis_url,
    backend=redis_url,
    include=[
        'tasks.google_maps_scraper',
        'tasks.linkedin_extractor', 
        'tasks.ecommerce_intelligence',
        'tasks.social_media_harvester',
        'tasks.real_estate_analyzer',
        'tasks.job_market_intelligence',
        'tasks.restaurant_analyzer',
        'tasks.finance_data_collector',
        'tasks.event_scout',
        'tasks.vehicle_market_intel',
        'tasks.seo_opportunity_finder',
        'tasks.health_checks',
        'tasks.cleanup_jobs'
    ]
)

# Celery Konfiguration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Berlin',
    enable_utc=True,
    
    # Task Routing
    task_routes={
        'tasks.google_maps_scraper.*': {'queue': 'scraping'},
        'tasks.linkedin_extractor.*': {'queue': 'scraping'},
        'tasks.ecommerce_intelligence.*': {'queue': 'scraping'},
        'tasks.social_media_harvester.*': {'queue': 'scraping'},
        'tasks.real_estate_analyzer.*': {'queue': 'scraping'},
        'tasks.job_market_intelligence.*': {'queue': 'scraping'},
        'tasks.restaurant_analyzer.*': {'queue': 'scraping'},
        'tasks.finance_data_collector.*': {'queue': 'scraping'},
        'tasks.event_scout.*': {'queue': 'scraping'},
        'tasks.vehicle_market_intel.*': {'queue': 'scraping'},
        'tasks.seo_opportunity_finder.*': {'queue': 'scraping'},
        'tasks.health_checks.*': {'queue': 'monitoring'},
        'tasks.cleanup_jobs.*': {'queue': 'maintenance'},
    },
    
    # Worker Konfiguration
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # Task Limits
    task_soft_time_limit=300,  # 5 Minuten
    task_time_limit=600,       # 10 Minuten
    
    # Result Backend
    result_expires=3600,       # 1 Stunde
    
    # Beat Schedule für periodische Tasks
    beat_schedule={
        # Health Checks alle 5 Minuten
        'health-check-all-services': {
            'task': 'tasks.health_checks.check_all_services',
            'schedule': 300.0,  # 5 Minuten
        },
        
        # Database Cleanup täglich um 2:00 Uhr
        'cleanup-old-data': {
            'task': 'tasks.cleanup_jobs.cleanup_old_records',
            'schedule': {
                'hour': 2,
                'minute': 0,
            },
        },
        
        # System Metrics alle 15 Minuten
        'collect-system-metrics': {
            'task': 'tasks.health_checks.collect_system_metrics',
            'schedule': 900.0,  # 15 Minuten
        },
        
        # Failed Tasks Retry alle 30 Minuten
        'retry-failed-tasks': {
            'task': 'tasks.cleanup_jobs.retry_failed_tasks',
            'schedule': 1800.0,  # 30 Minuten
        },
        
        # Auto-Lead-Generierung für Demo (stündlich)
        'auto-demo-leads': {
            'task': 'tasks.google_maps_scraper.auto_generate_demo_leads',
            'schedule': 3600.0,  # 1 Stunde
        },
    },
    beat_scheduler='django_celery_beat.schedulers:DatabaseScheduler',
)