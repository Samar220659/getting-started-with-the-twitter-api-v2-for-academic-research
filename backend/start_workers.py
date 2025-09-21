#!/usr/bin/env python3
"""
Celery Workers Starter für LeadMaps Automation
"""

import os
import sys
import subprocess
import signal
import time
import logging

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkerManager:
    """Manager für Celery Workers"""
    
    def __init__(self):
        self.processes = []
        self.running = False
        
        # Signal Handler
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Graceful Shutdown"""
        logger.info(f"Signal {signum} empfangen - Stoppe alle Worker...")
        self.stop_all_workers()
        sys.exit(0)
    
    def start_worker(self, queue_name, concurrency=2, loglevel='info'):
        """Einzelnen Worker starten"""
        try:
            cmd = [
                'celery', 
                '-A', 'celery_app',
                'worker',
                '--loglevel', loglevel,
                '--concurrency', str(concurrency),
                '--queues', queue_name,
                '--hostname', f'worker-{queue_name}@%h',
                '--logfile', f'/app/logs/worker_{queue_name}.log',
                '--pidfile', f'/app/logs/worker_{queue_name}.pid'
            ]
            
            logger.info(f"Starte Worker für Queue '{queue_name}' mit Concurrency {concurrency}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd='/app/backend'
            )
            
            self.processes.append({
                'queue': queue_name,
                'process': process,
                'pid': process.pid
            })
            
            logger.info(f"Worker für Queue '{queue_name}' gestartet - PID: {process.pid}")
            return process
            
        except Exception as e:
            logger.error(f"Fehler beim Starten des Workers für Queue '{queue_name}': {str(e)}")
            return None
    
    def start_beat_scheduler(self):
        """Beat Scheduler starten"""
        try:
            cmd = [
                'celery',
                '-A', 'celery_app', 
                'beat',
                '--loglevel', 'info',
                '--logfile', '/app/logs/celery_beat.log',
                '--pidfile', '/app/logs/celery_beat.pid'
            ]
            
            logger.info("Starte Celery Beat Scheduler...")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd='/app/backend'
            )
            
            self.processes.append({
                'queue': 'beat_scheduler',
                'process': process,
                'pid': process.pid
            })
            
            logger.info(f"Beat Scheduler gestartet - PID: {process.pid}")
            return process
            
        except Exception as e:
            logger.error(f"Fehler beim Starten des Beat Schedulers: {str(e)}")
            return None
    
    def start_all_workers(self):
        """Alle Worker und Services starten"""
        logger.info("Starte alle Celery Workers und Services...")
        
        # Worker-Konfiguration
        worker_configs = [
            {'queue': 'scraping', 'concurrency': 4},      # Haupt-Scraping-Tasks
            {'queue': 'monitoring', 'concurrency': 2},    # Health-Checks
            {'queue': 'maintenance', 'concurrency': 1},   # Cleanup-Jobs
            {'queue': 'default', 'concurrency': 2}        # Standard-Queue
        ]
        
        # Workers starten
        for config in worker_configs:
            self.start_worker(config['queue'], config['concurrency'])
            time.sleep(2)  # Kurze Pause zwischen Starts
        
        # Beat Scheduler starten
        self.start_beat_scheduler()
        
        self.running = True
        logger.info(f"Alle Services gestartet - {len(self.processes)} Prozesse aktiv")
    
    def monitor_processes(self):
        """Prozess-Monitoring"""
        while self.running:
            try:
                time.sleep(30)  # Check alle 30 Sekunden
                
                for worker_info in self.processes[:]:  # Copy für sichere Iteration
                    process = worker_info['process']
                    
                    # Prüfe ob Prozess noch läuft
                    poll_result = process.poll()
                    
                    if poll_result is not None:
                        # Prozess ist beendet
                        logger.warning(f"Worker {worker_info['queue']} (PID {worker_info['pid']}) ist beendet - Exit Code: {poll_result}")
                        
                        # Aus Liste entfernen
                        self.processes.remove(worker_info)
                        
                        # Bei Scraping und Default Workers: Neustart versuchen
                        if worker_info['queue'] in ['scraping', 'default']:
                            logger.info(f"Starte Worker {worker_info['queue']} neu...")
                            concurrency = 4 if worker_info['queue'] == 'scraping' else 2
                            self.start_worker(worker_info['queue'], concurrency)
                
                # Status-Log alle 5 Minuten
                current_time = time.time()
                if hasattr(self, '_last_status_log'):
                    if current_time - self._last_status_log > 300:
                        logger.info(f"Status: {len(self.processes)} aktive Worker-Prozesse")
                        self._last_status_log = current_time
                else:
                    self._last_status_log = current_time
                        
            except KeyboardInterrupt:
                logger.info("Monitoring unterbrochen")
                break
            except Exception as e:
                logger.error(f"Fehler im Prozess-Monitoring: {str(e)}")
                time.sleep(10)
    
    def stop_all_workers(self):
        """Alle Worker stoppen"""
        logger.info("Stoppe alle Worker-Prozesse...")
        
        self.running = False
        
        for worker_info in self.processes:
            try:
                process = worker_info['process']
                queue_name = worker_info['queue']
                
                if process.poll() is None:  # Prozess läuft noch
                    logger.info(f"Stoppe Worker {queue_name} (PID {process.pid})...")
                    
                    # Graceful shutdown versuchen
                    process.terminate()
                    
                    # Warten auf Beendigung (max 10 Sekunden)
                    try:
                        process.wait(timeout=10)
                        logger.info(f"Worker {queue_name} erfolgreich gestoppt")
                    except subprocess.TimeoutExpired:
                        logger.warning(f"Worker {queue_name} antwortet nicht - Force Kill...")
                        process.kill()
                        process.wait()
                        
            except Exception as e:
                logger.error(f"Fehler beim Stoppen von Worker {worker_info['queue']}: {str(e)}")
        
        self.processes.clear()
        logger.info("Alle Worker gestoppt")

def main():
    """Hauptfunktion"""
    print("🔧 LeadMaps Celery Workers Manager")
    print("=" * 50)
    
    # Log-Verzeichnis erstellen
    os.makedirs('/app/logs', exist_ok=True)
    
    manager = WorkerManager()
    
    try:
        # Alle Worker starten
        manager.start_all_workers()
        
        print("✅ Alle Worker gestartet - Monitoring aktiv...")
        print("📊 Logs verfügbar in: /app/logs/")
        print("⏹️  Strg+C zum Beenden")
        
        # Monitoring starten
        manager.monitor_processes()
        
    except KeyboardInterrupt:
        print("\n⚠️  Shutdown durch Benutzer initiiert")
    except Exception as e:
        logger.error(f"Kritischer Fehler: {str(e)}")
    finally:
        manager.stop_all_workers()
        print("✅ Worker Manager beendet")

if __name__ == "__main__":
    main()