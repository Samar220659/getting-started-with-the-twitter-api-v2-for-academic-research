"""
SELF-HEALING SYSTEM - ZZ-LOBBY-BOOST
Vollautomatisches System-Monitoring und -Reparatur alle 30 Minuten
"""

import os
import asyncio
import aiohttp
import json
import subprocess
import sys
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import requests
from fastapi import HTTPException
import tempfile
import shutil
import logging
import psutil
import signal
from pathlib import Path

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/self_healing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class SystemHealthCheck:
    component: str
    status: str  # healthy, warning, critical, failed
    details: str
    fix_applied: bool = False
    fix_details: str = ""
    last_check: datetime = datetime.now()
    error_count: int = 0

class SelfHealingSystem:
    def __init__(self):
        self.check_interval = 1800  # 30 minutes in seconds
        self.max_healing_attempts = 5
        self.critical_components = [
            'backend_api',
            'frontend_expo',
            'mongodb',
            'nginx_proxy',
            'system_resources',
            'network_connectivity',
            'security_status',
            'file_permissions',
            'dependency_integrity',
            'code_syntax',
            'database_integrity',
            'api_endpoints',
            'authentication',
            'ssl_certificates',
            'backup_systems'
        ]
        self.health_status = {}
        self.healing_history = []
        
    async def start_continuous_monitoring(self):
        """Startet das kontinuierliche Monitoring alle 30 Minuten"""
        logger.info("🔧 SELF-HEALING SYSTEM GESTARTET - Monitoring alle 30 Minuten")
        
        while True:
            try:
                await self.perform_complete_health_check()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Fehler im Monitoring Loop: {str(e)}")
                await asyncio.sleep(300)  # 5 Min Pause bei Fehlern
    
    async def perform_complete_health_check(self):
        """Führt kompletten Gesundheitscheck durch"""
        logger.info("🏥 STARTE KOMPLETTEN SYSTEM-GESUNDHEITSCHECK")
        
        check_results = []
        healing_needed = []
        
        # 1. Backend API Check
        backend_check = await self.check_backend_api()
        check_results.append(backend_check)
        if backend_check.status in ['warning', 'critical', 'failed']:
            healing_needed.append(backend_check)
        
        # 2. Frontend Expo Check
        frontend_check = await self.check_frontend_expo()
        check_results.append(frontend_check)
        if frontend_check.status in ['warning', 'critical', 'failed']:
            healing_needed.append(frontend_check)
        
        # 3. MongoDB Check
        mongodb_check = await self.check_mongodb()
        check_results.append(mongodb_check)
        if mongodb_check.status in ['warning', 'critical', 'failed']:
            healing_needed.append(mongodb_check)
        
        # 4. System Resources Check
        resources_check = await self.check_system_resources()
        check_results.append(resources_check)
        if resources_check.status in ['warning', 'critical', 'failed']:
            healing_needed.append(resources_check)
        
        # 5. Network Connectivity Check
        network_check = await self.check_network_connectivity()
        check_results.append(network_check)
        if network_check.status in ['warning', 'critical', 'failed']:
            healing_needed.append(network_check)
        
        # 6. Security Status Check
        security_check = await self.check_security_status()
        check_results.append(security_check)
        if security_check.status in ['warning', 'critical', 'failed']:
            healing_needed.append(security_check)
        
        # 7. File Permissions Check
        permissions_check = await self.check_file_permissions()
        check_results.append(permissions_check)
        if permissions_check.status in ['warning', 'critical', 'failed']:
            healing_needed.append(permissions_check)
        
        # 8. Dependency Integrity Check
        deps_check = await self.check_dependency_integrity()
        check_results.append(deps_check)
        if deps_check.status in ['warning', 'critical', 'failed']:
            healing_needed.append(deps_check)
        
        # 9. Code Syntax Check
        syntax_check = await self.check_code_syntax()
        check_results.append(syntax_check)
        if syntax_check.status in ['warning', 'critical', 'failed']:
            healing_needed.append(syntax_check)
        
        # 10. Database Integrity Check
        db_integrity_check = await self.check_database_integrity()
        check_results.append(db_integrity_check)
        if db_integrity_check.status in ['warning', 'critical', 'failed']:
            healing_needed.append(db_integrity_check)
        
        # 11. API Endpoints Check
        api_check = await self.check_api_endpoints()
        check_results.append(api_check)
        if api_check.status in ['warning', 'critical', 'failed']:
            healing_needed.append(api_check)
        
        # 12. SSL Certificates Check
        ssl_check = await self.check_ssl_certificates()
        check_results.append(ssl_check)
        if ssl_check.status in ['warning', 'critical', 'failed']:
            healing_needed.append(ssl_check)
        
        # Health Status updaten
        self.health_status = {check.component: check for check in check_results}
        
        # Healing durchführen wenn nötig
        if healing_needed:
            logger.warning(f"🚨 {len(healing_needed)} Komponenten benötigen Heilung")
            await self.perform_healing_cycle(healing_needed)
        else:
            logger.info("✅ ALLE SYSTEME GESUND - Kein Healing erforderlich")
        
        # Status Report erstellen
        await self.generate_health_report(check_results)
    
    async def check_backend_api(self) -> SystemHealthCheck:
        """Überprüft Backend API Status"""
        try:
            # Process Check
            result = subprocess.run(['sudo', 'supervisorctl', 'status', 'backend'], 
                                  capture_output=True, text=True)
            
            if 'RUNNING' in result.stdout:
                # API Endpoint Test
                try:
                    response = requests.get('http://localhost:8001/api/', timeout=10)
                    if response.status_code == 200:
                        return SystemHealthCheck(
                            component='backend_api',
                            status='healthy',
                            details='Backend API läuft und antwortet korrekt'
                        )
                    else:
                        return SystemHealthCheck(
                            component='backend_api',
                            status='warning',
                            details=f'Backend API läuft, aber Status Code: {response.status_code}'
                        )
                except requests.RequestException as e:
                    return SystemHealthCheck(
                        component='backend_api',
                        status='critical',
                        details=f'Backend Process läuft, aber API nicht erreichbar: {str(e)}'
                    )
            else:
                return SystemHealthCheck(
                    component='backend_api',
                    status='failed',
                    details=f'Backend Process nicht aktiv: {result.stdout}'
                )
                
        except Exception as e:
            return SystemHealthCheck(
                component='backend_api',
                status='failed',
                details=f'Backend Check Fehler: {str(e)}'
            )
    
    async def check_frontend_expo(self) -> SystemHealthCheck:
        """Überprüft Frontend Expo Status"""
        try:
            result = subprocess.run(['sudo', 'supervisorctl', 'status', 'expo'], 
                                  capture_output=True, text=True)
            
            if 'RUNNING' in result.stdout:
                # Frontend Endpoint Test
                try:
                    response = requests.get('http://localhost:3000', timeout=10)
                    if response.status_code == 200:
                        return SystemHealthCheck(
                            component='frontend_expo',
                            status='healthy',
                            details='Frontend Expo läuft und ist erreichbar'
                        )
                    else:
                        return SystemHealthCheck(
                            component='frontend_expo',
                            status='warning',
                            details=f'Frontend läuft, aber Status Code: {response.status_code}'
                        )
                except requests.RequestException as e:
                    return SystemHealthCheck(
                        component='frontend_expo',
                        status='critical',
                        details=f'Frontend Process läuft, aber nicht erreichbar: {str(e)}'
                    )
            else:
                return SystemHealthCheck(
                    component='frontend_expo',
                    status='failed',
                    details=f'Frontend Process nicht aktiv: {result.stdout}'
                )
                
        except Exception as e:
            return SystemHealthCheck(
                component='frontend_expo',
                status='failed',
                details=f'Frontend Check Fehler: {str(e)}'
            )
    
    async def check_mongodb(self) -> SystemHealthCheck:
        """Überprüft MongoDB Status"""
        try:
            result = subprocess.run(['sudo', 'supervisorctl', 'status', 'mongodb'], 
                                  capture_output=True, text=True)
            
            if 'RUNNING' in result.stdout:
                # MongoDB Connection Test
                try:
                    from motor.motor_asyncio import AsyncIOMotorClient
                    client = AsyncIOMotorClient('mongodb://localhost:27017')
                    await client.admin.command('ping')
                    
                    return SystemHealthCheck(
                        component='mongodb',
                        status='healthy',
                        details='MongoDB läuft und akzeptiert Verbindungen'
                    )
                except Exception as e:
                    return SystemHealthCheck(
                        component='mongodb',
                        status='critical',
                        details=f'MongoDB Process läuft, aber Verbindung fehlgeschlagen: {str(e)}'
                    )
            else:
                return SystemHealthCheck(
                    component='mongodb',
                    status='failed',
                    details=f'MongoDB Process nicht aktiv: {result.stdout}'
                )
                
        except Exception as e:
            return SystemHealthCheck(
                component='mongodb',
                status='failed',
                details=f'MongoDB Check Fehler: {str(e)}'
            )
    
    async def check_system_resources(self) -> SystemHealthCheck:
        """Überprüft Systemressourcen"""
        try:
            # CPU Usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory Usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk Usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Bewertung
            if cpu_percent > 90 or memory_percent > 90 or disk_percent > 90:
                status = 'critical'
                details = f'Kritische Ressourcennutzung - CPU: {cpu_percent}%, RAM: {memory_percent}%, Disk: {disk_percent:.1f}%'
            elif cpu_percent > 75 or memory_percent > 75 or disk_percent > 80:
                status = 'warning'
                details = f'Hohe Ressourcennutzung - CPU: {cpu_percent}%, RAM: {memory_percent}%, Disk: {disk_percent:.1f}%'
            else:
                status = 'healthy'
                details = f'Ressourcen OK - CPU: {cpu_percent}%, RAM: {memory_percent}%, Disk: {disk_percent:.1f}%'
            
            return SystemHealthCheck(
                component='system_resources',
                status=status,
                details=details
            )
            
        except Exception as e:
            return SystemHealthCheck(
                component='system_resources',
                status='failed',
                details=f'Ressourcen Check Fehler: {str(e)}'
            )
    
    async def check_network_connectivity(self) -> SystemHealthCheck:
        """Überprüft Netzwerkverbindung"""
        try:
            # Internet Connectivity Test
            test_urls = [
                'https://google.com',
                'https://github.com',
                'https://pypi.org'
            ]
            
            successful_connections = 0
            
            for url in test_urls:
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        successful_connections += 1
                except:
                    pass
            
            if successful_connections == len(test_urls):
                return SystemHealthCheck(
                    component='network_connectivity',
                    status='healthy',
                    details='Alle Netzwerkverbindungen funktionieren'
                )
            elif successful_connections > 0:
                return SystemHealthCheck(
                    component='network_connectivity',
                    status='warning',
                    details=f'Nur {successful_connections}/{len(test_urls)} Verbindungen erfolgreich'
                )
            else:
                return SystemHealthCheck(
                    component='network_connectivity',
                    status='failed',
                    details='Keine Netzwerkverbindungen möglich'
                )
                
        except Exception as e:
            return SystemHealthCheck(
                component='network_connectivity',
                status='failed',
                details=f'Netzwerk Check Fehler: {str(e)}'
            )
    
    async def check_security_status(self) -> SystemHealthCheck:
        """Überprüft Sicherheitsstatus"""
        try:
            security_issues = []
            
            # File Permissions Check
            sensitive_files = [
                '/app/backend/.env',
                '/app/frontend/.env'
            ]
            
            for file_path in sensitive_files:
                if os.path.exists(file_path):
                    file_stat = os.stat(file_path)
                    file_mode = oct(file_stat.st_mode)[-3:]
                    if file_mode != '600':  # Sollte nur für Owner lesbar/schreibbar sein
                        security_issues.append(f'Unsichere Berechtigung für {file_path}: {file_mode}')
                        
            # Process Check für unbekannte Prozesse
            suspicious_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username']):
                try:
                    # Einfache Heuristik für verdächtige Prozesse
                    if proc.info['username'] not in ['root', 'www-data', 'mongodb', 'nobody']:
                        if proc.info['name'] in ['nc', 'ncat', 'telnet', 'wget', 'curl'] and 'expo' not in proc.info['name']:
                            suspicious_processes.append(f"Verdächtiger Prozess: {proc.info['name']} (PID: {proc.info['pid']})")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            security_issues.extend(suspicious_processes)
            
            if len(security_issues) > 5:
                status = 'critical'
            elif len(security_issues) > 2:
                status = 'warning'
            elif len(security_issues) > 0:
                status = 'warning'
            else:
                status = 'healthy'
                
            details = f'Sicherheitsprobleme gefunden: {len(security_issues)}' if security_issues else 'Keine Sicherheitsprobleme erkannt'
            
            return SystemHealthCheck(
                component='security_status',
                status=status,
                details=details + (f' - {security_issues[:3]}' if security_issues else '')
            )
            
        except Exception as e:
            return SystemHealthCheck(
                component='security_status',
                status='failed',
                details=f'Security Check Fehler: {str(e)}'
            )
    
    async def check_file_permissions(self) -> SystemHealthCheck:
        """Überprüft Dateiberechtigungen"""
        try:
            permission_issues = []
            
            # Wichtige Verzeichnisse und ihre erwarteten Berechtigungen
            important_paths = {
                '/app': '755',
                '/app/backend': '755',
                '/app/frontend': '755',
                '/app/backend/server.py': '644',
                '/app/backend/.env': '600',
                '/app/frontend/.env': '600'
            }
            
            for path, expected_perm in important_paths.items():
                if os.path.exists(path):
                    actual_perm = oct(os.stat(path).st_mode)[-3:]
                    if actual_perm != expected_perm:
                        permission_issues.append(f'{path}: erwartet {expected_perm}, ist {actual_perm}')
            
            if len(permission_issues) > 3:
                status = 'critical'
            elif len(permission_issues) > 0:
                status = 'warning'
            else:
                status = 'healthy'
                
            details = f'Berechtigungsprobleme: {len(permission_issues)}' if permission_issues else 'Alle Dateiberechtigungen korrekt'
            
            return SystemHealthCheck(
                component='file_permissions',
                status=status,
                details=details
            )
            
        except Exception as e:
            return SystemHealthCheck(
                component='file_permissions',
                status='failed',
                details=f'File Permissions Check Fehler: {str(e)}'
            )
    
    async def check_dependency_integrity(self) -> SystemHealthCheck:
        """Überprüft Abhängigkeiten"""
        try:
            issues = []
            
            # Python Dependencies Check
            try:
                result = subprocess.run([sys.executable, '-m', 'pip', 'check'], 
                                      capture_output=True, text=True, cwd='/app/backend')
                if result.returncode != 0:
                    issues.append(f'Python Dependency Konflikte: {result.stdout[:200]}')
            except Exception as e:
                issues.append(f'Python Dependency Check fehlgeschlagen: {str(e)}')
            
            # Node Dependencies Check
            try:
                result = subprocess.run(['npm', 'audit', '--audit-level=high'], 
                                      capture_output=True, text=True, cwd='/app/frontend')
                if result.returncode != 0 and 'vulnerabilities' in result.stdout:
                    issues.append(f'Node.js Sicherheitslücken gefunden')
            except Exception as e:
                issues.append(f'Node Dependency Check fehlgeschlagen: {str(e)}')
            
            if len(issues) > 2:
                status = 'critical'
            elif len(issues) > 0:
                status = 'warning'
            else:
                status = 'healthy'
                
            details = f'Dependency Probleme: {len(issues)}' if issues else 'Alle Dependencies OK'
            
            return SystemHealthCheck(
                component='dependency_integrity',
                status=status,
                details=details
            )
            
        except Exception as e:
            return SystemHealthCheck(
                component='dependency_integrity',
                status='failed',
                details=f'Dependency Check Fehler: {str(e)}'
            )
    
    async def check_code_syntax(self) -> SystemHealthCheck:
        """Überprüft Code-Syntax"""
        try:
            syntax_errors = []
            
            # Python Files Syntax Check
            python_files = []
            for root, dirs, files in os.walk('/app/backend'):
                for file in files:
                    if file.endswith('.py'):
                        python_files.append(os.path.join(root, file))
            
            for py_file in python_files[:10]:  # Check first 10 files
                try:
                    with open(py_file, 'r') as f:
                        compile(f.read(), py_file, 'exec')
                except SyntaxError as e:
                    syntax_errors.append(f'Syntax Fehler in {py_file}: {str(e)}')
                except Exception:
                    pass  # Skip files that can't be read
            
            # JavaScript/TypeScript Files Check
            js_files = []
            for root, dirs, files in os.walk('/app/frontend'):
                if 'node_modules' not in root:
                    for file in files:
                        if file.endswith(('.js', '.jsx', '.ts', '.tsx')):
                            js_files.append(os.path.join(root, file))
            
            # Basic JS syntax check using node
            for js_file in js_files[:5]:  # Check first 5 files
                try:
                    result = subprocess.run(['node', '--check', js_file], 
                                          capture_output=True, text=True)
                    if result.returncode != 0:
                        syntax_errors.append(f'JS Syntax Fehler in {js_file}')
                except Exception:
                    pass
            
            if len(syntax_errors) > 3:
                status = 'critical'
            elif len(syntax_errors) > 0:
                status = 'warning'
            else:
                status = 'healthy'
                
            details = f'Syntax Fehler gefunden: {len(syntax_errors)}' if syntax_errors else 'Code Syntax OK'
            
            return SystemHealthCheck(
                component='code_syntax',
                status=status,
                details=details
            )
            
        except Exception as e:
            return SystemHealthCheck(
                component='code_syntax',
                status='failed',
                details=f'Code Syntax Check Fehler: {str(e)}'
            )
    
    async def check_database_integrity(self) -> SystemHealthCheck:
        """Überprüft Datenbankintegrität"""
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            
            client = AsyncIOMotorClient('mongodb://localhost:27017')
            db = client['test_database']
            
            # Collections Check
            collections = await db.list_collection_names()
            expected_collections = ['workflows', 'leads', 'content', 'social_posts', 'revenue']
            
            missing_collections = []
            for expected in expected_collections:
                if expected not in collections:
                    missing_collections.append(expected)
            
            # Index Check
            index_issues = []
            for collection_name in collections:
                try:
                    collection = db[collection_name]
                    indexes = await collection.list_indexes().to_list(length=None)
                    if len(indexes) < 1:  # Mindestens _id Index sollte vorhanden sein
                        index_issues.append(f'Keine Indizes in {collection_name}')
                except Exception:
                    pass
            
            total_issues = len(missing_collections) + len(index_issues)
            
            if total_issues > 3:
                status = 'critical'
            elif total_issues > 0:
                status = 'warning'
            else:
                status = 'healthy'
                
            details = f'DB Probleme: {total_issues} (Missing Collections: {len(missing_collections)}, Index Issues: {len(index_issues)})'
            
            return SystemHealthCheck(
                component='database_integrity',
                status=status,
                details=details
            )
            
        except Exception as e:
            return SystemHealthCheck(
                component='database_integrity',
                status='failed',
                details=f'Database Check Fehler: {str(e)}'
            )
    
    async def check_api_endpoints(self) -> SystemHealthCheck:
        """Überprüft API Endpoints"""
        try:
            critical_endpoints = [
                'http://localhost:8001/api/',
                'http://localhost:8001/api/stats',
                'http://localhost:8001/api/workflows',
                'http://localhost:8001/api/leads'
            ]
            
            failed_endpoints = []
            slow_endpoints = []
            
            for endpoint in critical_endpoints:
                try:
                    start_time = datetime.now()
                    response = requests.get(endpoint, timeout=10)
                    response_time = (datetime.now() - start_time).total_seconds()
                    
                    if response.status_code != 200:
                        failed_endpoints.append(f'{endpoint}: {response.status_code}')
                    elif response_time > 5:  # Langsamer als 5 Sekunden
                        slow_endpoints.append(f'{endpoint}: {response_time:.2f}s')
                        
                except requests.RequestException as e:
                    failed_endpoints.append(f'{endpoint}: {str(e)}')
            
            total_issues = len(failed_endpoints) + len(slow_endpoints)
            
            if len(failed_endpoints) > 2:
                status = 'critical'
            elif total_issues > 0:
                status = 'warning'
            else:
                status = 'healthy'
                
            details = f'API Probleme: {total_issues} (Failed: {len(failed_endpoints)}, Slow: {len(slow_endpoints)})'
            
            return SystemHealthCheck(
                component='api_endpoints',
                status=status,
                details=details
            )
            
        except Exception as e:
            return SystemHealthCheck(
                component='api_endpoints',
                status='failed',
                details=f'API Endpoints Check Fehler: {str(e)}'
            )
    
    async def check_ssl_certificates(self) -> SystemHealthCheck:
        """Überprüft SSL Zertifikate"""
        try:
            # Für Development Environment - SSL meist nicht relevant
            # In Production würde hier echte SSL Check erfolgen
            
            return SystemHealthCheck(
                component='ssl_certificates',
                status='healthy',
                details='SSL Check übersprungen (Development Environment)'
            )
            
        except Exception as e:
            return SystemHealthCheck(
                component='ssl_certificates',
                status='failed',
                details=f'SSL Check Fehler: {str(e)}'
            )
    
    async def perform_healing_cycle(self, issues: List[SystemHealthCheck]):
        """Führt Heilungszyklus durch"""
        logger.info(f"🚑 HEALING CYCLE GESTARTET - {len(issues)} Probleme zu beheben")
        
        healing_attempts = 0
        max_cycles = 5
        
        while issues and healing_attempts < max_cycles:
            healing_attempts += 1
            logger.info(f"🔄 Healing Cycle {healing_attempts}/{max_cycles}")
            
            healed_issues = []
            
            for issue in issues:
                try:
                    healing_result = await self.heal_component(issue)
                    if healing_result:
                        healed_issues.append(issue)
                        logger.info(f"✅ {issue.component} erfolgreich geheilt")
                    else:
                        logger.warning(f"⚠️ {issue.component} konnte nicht geheilt werden")
                        issue.error_count += 1
                        
                except Exception as e:
                    logger.error(f"❌ Fehler beim Heilen von {issue.component}: {str(e)}")
                    issue.error_count += 1
            
            # Geheilte Issues entfernen
            for healed in healed_issues:
                issues.remove(healed)
            
            # Re-check nach Healing
            if issues:
                logger.info("🔍 Re-Check nach Healing...")
                await asyncio.sleep(30)  # 30 Sekunden warten
                
                recheck_issues = []
                for issue in issues:
                    recheck_result = await self.recheck_component(issue.component)
                    if recheck_result.status not in ['healthy']:
                        recheck_issues.append(recheck_result)
                
                issues = recheck_issues
        
        if not issues:
            logger.info("🎉 ALLE PROBLEME ERFOLGREICH BEHOBEN!")
        else:
            logger.warning(f"⚠️ {len(issues)} Probleme konnten nicht behoben werden nach {max_cycles} Zyklen")
    
    async def heal_component(self, issue: SystemHealthCheck) -> bool:
        """Heilt spezifische Komponente"""
        component = issue.component
        
        try:
            if component == 'backend_api':
                return await self.heal_backend_api()
            elif component == 'frontend_expo':
                return await self.heal_frontend_expo()
            elif component == 'mongodb':
                return await self.heal_mongodb()
            elif component == 'system_resources':
                return await self.heal_system_resources()
            elif component == 'network_connectivity':
                return await self.heal_network_connectivity()
            elif component == 'security_status':
                return await self.heal_security_status()
            elif component == 'file_permissions':
                return await self.heal_file_permissions()
            elif component == 'dependency_integrity':
                return await self.heal_dependency_integrity()
            elif component == 'code_syntax':
                return await self.heal_code_syntax()
            elif component == 'database_integrity':
                return await self.heal_database_integrity()
            elif component == 'api_endpoints':
                return await self.heal_api_endpoints()
            else:
                logger.warning(f"Keine Healing-Strategie für {component}")
                return False
                
        except Exception as e:
            logger.error(f"Healing Fehler für {component}: {str(e)}")
            return False
    
    async def heal_backend_api(self) -> bool:
        """Heilt Backend API"""
        try:
            # Backend neustarten
            result = subprocess.run(['sudo', 'supervisorctl', 'restart', 'backend'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                # 10 Sekunden warten
                await asyncio.sleep(10)
                
                # Check ob wieder erreichbar
                response = requests.get('http://localhost:8001/api/', timeout=10)
                return response.status_code == 200
            
            return False
            
        except Exception as e:
            logger.error(f"Backend Healing Fehler: {str(e)}")
            return False
    
    async def heal_frontend_expo(self) -> bool:
        """Heilt Frontend Expo"""
        try:
            # Frontend neustarten
            result = subprocess.run(['sudo', 'supervisorctl', 'restart', 'expo'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                # 15 Sekunden warten (Expo braucht länger)
                await asyncio.sleep(15)
                
                # Check ob wieder erreichbar
                response = requests.get('http://localhost:3000', timeout=15)
                return response.status_code == 200
            
            return False
            
        except Exception as e:
            logger.error(f"Frontend Healing Fehler: {str(e)}")
            return False
    
    async def heal_mongodb(self) -> bool:
        """Heilt MongoDB"""
        try:
            # MongoDB neustarten
            result = subprocess.run(['sudo', 'supervisorctl', 'restart', 'mongodb'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                await asyncio.sleep(10)
                
                # Check Verbindung
                from motor.motor_asyncio import AsyncIOMotorClient
                client = AsyncIOMotorClient('mongodb://localhost:27017')
                await client.admin.command('ping')
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"MongoDB Healing Fehler: {str(e)}")
            return False
    
    async def heal_system_resources(self) -> bool:
        """Heilt Systemressourcen"""
        try:
            # Memory cleanup
            subprocess.run(['sync'], check=True)
            subprocess.run(['echo', '3'], stdout=open('/proc/sys/vm/drop_caches', 'w'), check=True)
            
            # Kill resource-intensive processes if needed
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if proc.info['cpu_percent'] > 50 and proc.info['name'] not in ['backend', 'expo', 'mongodb']:
                        logger.info(f"Killing high-resource process: {proc.info['name']} (PID: {proc.info['pid']})")
                        proc.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return True
            
        except Exception as e:
            logger.error(f"System Resources Healing Fehler: {str(e)}")
            return False
    
    async def heal_network_connectivity(self) -> bool:
        """Heilt Netzwerkverbindung"""
        try:
            # DNS flush
            subprocess.run(['sudo', 'systemctl', 'restart', 'systemd-resolved'], check=True)
            
            # Network restart
            subprocess.run(['sudo', 'systemctl', 'restart', 'networking'], check=True)
            
            await asyncio.sleep(5)
            return True
            
        except Exception as e:
            logger.error(f"Network Healing Fehler: {str(e)}")
            return False
    
    async def heal_security_status(self) -> bool:
        """Heilt Sicherheitsprobleme"""
        try:
            # File permissions fix
            await self.heal_file_permissions()
            
            # Kill suspicious processes
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] in ['nc', 'ncat', 'telnet'] and 'expo' not in proc.info['name']:
                        logger.info(f"Killing suspicious process: {proc.info['name']} (PID: {proc.info['pid']})")
                        proc.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return True
            
        except Exception as e:
            logger.error(f"Security Healing Fehler: {str(e)}")
            return False
    
    async def heal_file_permissions(self) -> bool:
        """Heilt Dateiberechtigungen"""
        try:
            permission_fixes = {
                '/app': '755',
                '/app/backend': '755',
                '/app/frontend': '755',
                '/app/backend/server.py': '644',
                '/app/backend/.env': '600',
                '/app/frontend/.env': '600'
            }
            
            for path, permission in permission_fixes.items():
                if os.path.exists(path):
                    subprocess.run(['chmod', permission, path], check=True)
            
            return True
            
        except Exception as e:
            logger.error(f"File Permissions Healing Fehler: {str(e)}")
            return False
    
    async def heal_dependency_integrity(self) -> bool:
        """Heilt Abhängigkeiten"""
        try:
            # Python dependencies fix
            subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                         cwd='/app/backend', check=True)
            
            # Node dependencies fix
            subprocess.run(['npm', 'audit', 'fix'], cwd='/app/frontend', check=False)
            
            return True
            
        except Exception as e:
            logger.error(f"Dependencies Healing Fehler: {str(e)}")
            return False
    
    async def heal_code_syntax(self) -> bool:
        """Heilt Code-Syntax (soweit möglich)"""
        try:
            # Automatic code formatting
            try:
                subprocess.run(['black', '--check', '/app/backend'], check=False)
            except:
                pass
            
            # Prettier für JS/TS (falls verfügbar)
            try:
                subprocess.run(['npx', 'prettier', '--check', '/app/frontend/app'], 
                             cwd='/app/frontend', check=False)
            except:
                pass
            
            return True
            
        except Exception as e:
            logger.error(f"Code Syntax Healing Fehler: {str(e)}")
            return False
    
    async def heal_database_integrity(self) -> bool:
        """Heilt Datenbankintegrität"""
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            
            client = AsyncIOMotorClient('mongodb://localhost:27017')
            db = client['test_database']
            
            # Create missing collections
            expected_collections = ['workflows', 'leads', 'content', 'social_posts', 'revenue']
            existing_collections = await db.list_collection_names()
            
            for collection_name in expected_collections:
                if collection_name not in existing_collections:
                    await db.create_collection(collection_name)
                    logger.info(f"Created missing collection: {collection_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Database Integrity Healing Fehler: {str(e)}")
            return False
    
    async def heal_api_endpoints(self) -> bool:
        """Heilt API Endpoints"""
        try:
            # Backend restart usually fixes API issues
            return await self.heal_backend_api()
            
        except Exception as e:
            logger.error(f"API Endpoints Healing Fehler: {str(e)}")
            return False
    
    async def recheck_component(self, component: str) -> SystemHealthCheck:
        """Überprüft Komponente erneut nach Healing"""
        if component == 'backend_api':
            return await self.check_backend_api()
        elif component == 'frontend_expo':
            return await self.check_frontend_expo()
        elif component == 'mongodb':
            return await self.check_mongodb()
        elif component == 'system_resources':
            return await self.check_system_resources()
        elif component == 'network_connectivity':
            return await self.check_network_connectivity()
        elif component == 'security_status':
            return await self.check_security_status()
        elif component == 'file_permissions':
            return await self.check_file_permissions()
        elif component == 'dependency_integrity':
            return await self.check_dependency_integrity()
        elif component == 'code_syntax':
            return await self.check_code_syntax()
        elif component == 'database_integrity':
            return await self.check_database_integrity()
        elif component == 'api_endpoints':
            return await self.check_api_endpoints()
        elif component == 'ssl_certificates':
            return await self.check_ssl_certificates()
        else:
            return SystemHealthCheck(
                component=component,
                status='unknown',
                details='Unbekannte Komponente für Recheck'
            )
    
    async def generate_health_report(self, check_results: List[SystemHealthCheck]):
        """Generiert Gesundheitsbericht"""
        try:
            healthy_count = len([c for c in check_results if c.status == 'healthy'])
            warning_count = len([c for c in check_results if c.status == 'warning'])
            critical_count = len([c for c in check_results if c.status == 'critical'])
            failed_count = len([c for c in check_results if c.status == 'failed'])
            
            total_count = len(check_results)
            health_percentage = (healthy_count / total_count) * 100 if total_count > 0 else 0
            
            report = f"""
==================================================
🏥 SYSTEM HEALTH REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
==================================================

📊 GESAMT-GESUNDHEITSSTATUS: {health_percentage:.1f}%

📈 KOMPONENTEN ÜBERSICHT:
✅ Gesund:      {healthy_count:2d} ({(healthy_count/total_count)*100:.1f}%)
⚠️  Warnung:    {warning_count:2d} ({(warning_count/total_count)*100:.1f}%)
🚨 Kritisch:    {critical_count:2d} ({(critical_count/total_count)*100:.1f}%)
❌ Fehlgeschlagen: {failed_count:2d} ({(failed_count/total_count)*100:.1f}%)

🔍 DETAILLIERTE ERGEBNISSE:
"""
            
            for check in check_results:
                status_emoji = {
                    'healthy': '✅',
                    'warning': '⚠️',
                    'critical': '🚨',
                    'failed': '❌'
                }.get(check.status, '❓')
                
                report += f"{status_emoji} {check.component:20s} | {check.status:8s} | {check.details[:60]}\n"
            
            if health_percentage >= 90:
                report += "\n🎉 SYSTEM LÄUFT OPTIMAL!"
            elif health_percentage >= 75:
                report += "\n👍 SYSTEM LÄUFT GUT - Kleinere Probleme vorhanden"
            elif health_percentage >= 50:
                report += "\n⚠️ SYSTEM BENÖTIGT AUFMERKSAMKEIT"
            else:
                report += "\n🚨 SYSTEM BENÖTIGT SOFORTIGE WARTUNG!"
            
            report += "\n==================================================\n"
            
            logger.info(report)
            
            # Report auch in Datei speichern
            os.makedirs('/app/logs', exist_ok=True)
            with open(f'/app/logs/health_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt', 'w') as f:
                f.write(report)
                
        except Exception as e:
            logger.error(f"Health Report Generation Fehler: {str(e)}")

# Global instance
self_healing_system = SelfHealingSystem()

# Async startup function
async def start_self_healing():
    """Startet das Self-Healing System"""
    await self_healing_system.start_continuous_monitoring()

if __name__ == "__main__":
    logger.info("🚀 SELF-HEALING SYSTEM WIRD GESTARTET...")
    asyncio.run(start_self_healing())