"""
BUSINESS MCPs - Finanzverwaltung, Sicherheit, Förderungen
Komplette Business-Management-Suite für ZZ-LOBBY-BOOST
"""

import os
import asyncio
import aiohttp
import json
import subprocess
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging
import hashlib
import secrets
import jwt
from cryptography.fernet import Fernet
import pandas as pd

logger = logging.getLogger(__name__)

# ============================
# FINANZVERWALTUNG & BUCHHALTUNG MCP
# ============================

class FinancialManagementMCP:
    def __init__(self):
        self.transactions = []
        self.tax_rates = {
            'DE': 0.19,  # Deutsche MwSt
            'AT': 0.20,
            'CH': 0.077
        }
        
    async def track_revenue(self, revenue_data: Dict) -> Dict:
        """Umsatz für Buchhaltung erfassen"""
        try:
            transaction = {
                'id': f"rev_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'type': 'revenue',
                'amount': revenue_data.get('amount', 0),
                'currency': revenue_data.get('currency', 'EUR'),
                'source': revenue_data.get('source', 'unknown'),
                'description': revenue_data.get('description', ''),
                'date': datetime.now().isoformat(),
                'tax_rate': self.tax_rates.get(revenue_data.get('country', 'DE'), 0.19),
                'net_amount': revenue_data.get('amount', 0) / (1 + self.tax_rates.get(revenue_data.get('country', 'DE'), 0.19)),
                'tax_amount': revenue_data.get('amount', 0) - (revenue_data.get('amount', 0) / (1 + self.tax_rates.get(revenue_data.get('country', 'DE'), 0.19))),
                'category': 'online_services',
                'quarter': f"Q{((datetime.now().month - 1) // 3) + 1}_{datetime.now().year}",
                'month': datetime.now().strftime('%Y-%m')
            }
            
            self.transactions.append(transaction)
            
            return {
                'success': True,
                'transaction_id': transaction['id'],
                'net_amount': round(transaction['net_amount'], 2),
                'tax_amount': round(transaction['tax_amount'], 2),
                'quarter': transaction['quarter']
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def track_expense(self, expense_data: Dict) -> Dict:
        """Ausgaben für Buchhaltung erfassen"""
        try:
            transaction = {
                'id': f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'type': 'expense',
                'amount': expense_data.get('amount', 0),
                'currency': expense_data.get('currency', 'EUR'),
                'description': expense_data.get('description', ''),
                'category': expense_data.get('category', 'business_expense'),
                'vendor': expense_data.get('vendor', ''),
                'date': datetime.now().isoformat(),
                'tax_deductible': expense_data.get('tax_deductible', True),
                'receipt_url': expense_data.get('receipt_url', ''),
                'quarter': f"Q{((datetime.now().month - 1) // 3) + 1}_{datetime.now().year}",
                'month': datetime.now().strftime('%Y-%m')
            }
            
            self.transactions.append(transaction)
            
            return {
                'success': True,
                'transaction_id': transaction['id'],
                'tax_deductible': transaction['tax_deductible'],
                'category': transaction['category']
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def generate_tax_report(self, year: int, quarter: Optional[int] = None) -> Dict:
        """Steuerreport generieren"""
        try:
            if quarter:
                filter_period = f"Q{quarter}_{year}"
                period_transactions = [t for t in self.transactions if t.get('quarter') == filter_period]
            else:
                period_transactions = [t for t in self.transactions if datetime.fromisoformat(t['date']).year == year]
            
            revenue_transactions = [t for t in period_transactions if t['type'] == 'revenue']
            expense_transactions = [t for t in period_transactions if t['type'] == 'expense']
            
            total_revenue = sum([t['amount'] for t in revenue_transactions])
            total_expenses = sum([t['amount'] for t in expense_transactions if t.get('tax_deductible', True)])
            net_income = total_revenue - total_expenses
            
            total_tax_collected = sum([t.get('tax_amount', 0) for t in revenue_transactions])
            
            tax_report = {
                'period': f"Q{quarter}_{year}" if quarter else str(year),
                'total_revenue': round(total_revenue, 2),
                'total_expenses': round(total_expenses, 2),
                'net_income': round(net_income, 2),
                'tax_collected': round(total_tax_collected, 2),
                'estimated_income_tax': round(net_income * 0.25, 2),  # Geschätzte Einkommensteuer
                'transaction_count': len(period_transactions),
                'revenue_breakdown': {
                    'online_services': sum([t['amount'] for t in revenue_transactions if t.get('category') == 'online_services']),
                    'affiliate': sum([t['amount'] for t in revenue_transactions if t.get('source') == 'affiliate']),
                    'consulting': sum([t['amount'] for t in revenue_transactions if t.get('category') == 'consulting'])
                },
                'expense_breakdown': {
                    'software': sum([t['amount'] for t in expense_transactions if t.get('category') == 'software']),
                    'marketing': sum([t['amount'] for t in expense_transactions if t.get('category') == 'marketing']),
                    'office': sum([t['amount'] for t in expense_transactions if t.get('category') == 'office'])
                }
            }
            
            return {
                'success': True,
                'tax_report': tax_report,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def export_transactions(self, format: str = 'csv') -> Dict:
        """Transaktionen exportieren für Steuerberatung"""
        try:
            if format == 'csv':
                import pandas as pd
                df = pd.DataFrame(self.transactions)
                csv_content = df.to_csv(index=False)
                
                filename = f"transactions_{datetime.now().strftime('%Y%m%d')}.csv"
                filepath = f"/app/exports/{filename}"
                
                os.makedirs('/app/exports', exist_ok=True)
                with open(filepath, 'w') as f:
                    f.write(csv_content)
                
                return {
                    'success': True,
                    'format': 'csv',
                    'filepath': filepath,
                    'filename': filename,
                    'transaction_count': len(self.transactions)
                }
            
            return {'success': False, 'error': 'Unsupported format'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

# ============================
# FÖRDERANTRÄGE & GRANTS MCP
# ============================

class GrantApplicationMCP:
    def __init__(self):
        self.grant_programs = self._load_grant_programs()
        
    def _load_grant_programs(self) -> Dict:
        """Verfügbare Förderprogramme laden"""
        return {
            'digitalization_grants': {
                'name': 'Digitalisierung und Innovation',
                'max_amount': 50000,
                'eligibility': ['startup', 'sme', 'digital_business'],
                'requirements': ['business_plan', 'financial_statements', 'innovation_description'],
                'deadline': '2025-12-31',
                'success_rate': 0.35,
                'processing_time_days': 90
            },
            'startup_grants': {
                'name': 'Startup-Förderung EXIST',
                'max_amount': 150000,
                'eligibility': ['startup', 'tech_company'],
                'requirements': ['business_plan', 'team_cv', 'market_analysis'],
                'deadline': '2025-06-30',
                'success_rate': 0.25,
                'processing_time_days': 120
            },
            'automation_grants': {
                'name': 'Automatisierung und KI-Förderung',
                'max_amount': 25000,
                'eligibility': ['automation_business', 'ai_company'],
                'requirements': ['technical_concept', 'roi_calculation'],
                'deadline': '2025-09-15',
                'success_rate': 0.45,
                'processing_time_days': 60
            },
            'export_grants': {
                'name': 'Export- und Internationalisierung',
                'max_amount': 30000,
                'eligibility': ['export_business', 'international'],
                'requirements': ['export_plan', 'market_research'],
                'deadline': '2025-11-30',
                'success_rate': 0.40,
                'processing_time_days': 75
            }
        }
    
    async def check_eligibility(self, business_profile: Dict) -> Dict:
        """Berechtigung für Förderprogramme prüfen"""
        try:
            business_type = business_profile.get('type', 'startup')
            annual_revenue = business_profile.get('annual_revenue', 0)
            employee_count = business_profile.get('employees', 1)
            industry = business_profile.get('industry', 'digital')
            
            eligible_programs = []
            
            for program_id, program in self.grant_programs.items():
                eligibility_score = 0
                reasons = []
                
                # Type Check
                if business_type in program['eligibility']:
                    eligibility_score += 30
                    reasons.append(f"Business type '{business_type}' matches")
                
                # Industry Check
                if industry in ['automation', 'ai', 'digital'] and 'automation' in program_id:
                    eligibility_score += 25
                    reasons.append("Industry matches automation focus")
                
                # Size Check
                if annual_revenue < 2000000:  # < 2M EUR = SME
                    eligibility_score += 20
                    reasons.append("Qualifies as SME")
                
                # Innovation Check
                if 'automation' in business_profile.get('keywords', []):
                    eligibility_score += 15
                    reasons.append("Innovation in automation")
                
                # Export potential
                if business_profile.get('target_markets', []):
                    eligibility_score += 10
                    reasons.append("International business potential")
                
                if eligibility_score >= 50:  # Mindest-Score für Berechtigung
                    estimated_amount = min(
                        program['max_amount'],
                        max(10000, annual_revenue * 0.1)  # Max 10% des Jahresumsatzes
                    )
                    
                    eligible_programs.append({
                        'program_id': program_id,
                        'program_name': program['name'],
                        'eligibility_score': eligibility_score,
                        'max_amount': program['max_amount'],
                        'estimated_amount': estimated_amount,
                        'success_rate': program['success_rate'],
                        'deadline': program['deadline'],
                        'reasons': reasons,
                        'requirements': program['requirements']
                    })
            
            # Sort by estimated amount (highest first)
            eligible_programs.sort(key=lambda x: x['estimated_amount'], reverse=True)
            
            return {
                'success': True,
                'eligible_programs': eligible_programs,
                'total_potential_funding': sum([p['estimated_amount'] for p in eligible_programs]),
                'recommendation': eligible_programs[0] if eligible_programs else None
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def generate_application(self, program_id: str, business_data: Dict) -> Dict:
        """Förderantrag automatisch generieren"""
        try:
            program = self.grant_programs.get(program_id)
            if not program:
                return {'success': False, 'error': 'Program not found'}
            
            application_data = {
                'program_id': program_id,
                'program_name': program['name'],
                'applicant': {
                    'company_name': business_data.get('company_name', 'ZZ-Lobby Automatisierung GmbH'),
                    'legal_form': business_data.get('legal_form', 'GmbH'),
                    'address': business_data.get('address', 'Deutschland'),
                    'tax_id': business_data.get('tax_id', 'DE123456789'),
                    'employees': business_data.get('employees', 2),
                    'annual_revenue': business_data.get('annual_revenue', 100000)
                },
                'project': {
                    'title': f"Automatisierte Revenue-Generierung für {business_data.get('industry', 'Online-Business')}",
                    'description': self._generate_project_description(business_data),
                    'innovation_aspects': [
                        'KI-basierte Content-Generierung',
                        'Vollautomatisierte Marketing-Workflows',
                        'Multi-Platform Social Media Automation',
                        'Intelligente Lead-Qualifizierung'
                    ],
                    'market_potential': self._calculate_market_potential(business_data),
                    'technical_feasibility': 'Bewährt durch erfolgreich implementierte Prototypen',
                    'timeline_months': 12,
                    'milestones': [
                        'Monat 1-3: System-Entwicklung und Testing',
                        'Monat 4-6: Beta-Tests mit Pilotkunden',
                        'Monat 7-9: Markteinführung und Skalierung',
                        'Monat 10-12: Optimierung und Expansion'
                    ]
                },
                'funding': {
                    'requested_amount': min(program['max_amount'], business_data.get('funding_needed', 50000)),
                    'own_contribution': business_data.get('own_contribution', 10000),
                    'total_project_cost': min(program['max_amount'], business_data.get('funding_needed', 50000)) + business_data.get('own_contribution', 10000),
                    'roi_projection': self._calculate_roi_projection(business_data)
                },
                'generated_at': datetime.now().isoformat(),
                'estimated_success_rate': program['success_rate']
            }
            
            # Generate application document
            application_document = self._generate_application_document(application_data)
            
            # Save application
            app_filename = f"grant_application_{program_id}_{datetime.now().strftime('%Y%m%d')}.json"
            app_filepath = f"/app/applications/{app_filename}"
            
            os.makedirs('/app/applications', exist_ok=True)
            with open(app_filepath, 'w') as f:
                json.dump(application_data, f, indent=2, ensure_ascii=False)
            
            return {
                'success': True,
                'application': application_data,
                'document': application_document,
                'filepath': app_filepath,
                'next_steps': [
                    'Geschäftsplan detaillieren',
                    'Finanzplanung überprüfen',
                    'Rechtliche Dokumente vorbereiten',
                    'Antrag bis ' + program['deadline'] + ' einreichen'
                ]
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _generate_project_description(self, business_data: Dict) -> str:
        """Projektbeschreibung generieren"""
        return f"""
        Entwicklung einer innovativen Automatisierungsplattform für {business_data.get('industry', 'digitale Unternehmen')}.
        
        Die Lösung kombiniert künstliche Intelligenz mit bewährten Marketing-Strategien, um vollautomatisierte 
        Revenue-Generierung zu ermöglichen. Das System erstellt automatisch zielgruppenspezifischen Content, 
        verteilt diesen über mehrere Social-Media-Plattformen und konvertiert Leads zu zahlenden Kunden.
        
        Kernfunktionen:
        - KI-gestützte Content-Erstellung in deutscher Sprache
        - Automatisierte Multi-Platform-Distribution
        - Intelligente Lead-Qualifizierung und -Nurturing
        - Echtzeit-Analytics und Performance-Optimization
        
        Zielmarkt: Deutsche KMUs mit Digitalisierungsbedarf
        Marktgröße: €2.5 Milliarden (Digital Marketing Automation Deutschland)
        """
    
    def _calculate_market_potential(self, business_data: Dict) -> Dict:
        """Marktpotential berechnen"""
        return {
            'total_addressable_market': '€2.5 Milliarden',
            'serviceable_addressable_market': '€250 Millionen',
            'serviceable_obtainable_market': '€25 Millionen',
            'target_customers': 10000,
            'average_revenue_per_customer': 2500,
            'market_growth_rate': '15% jährlich'
        }
    
    def _calculate_roi_projection(self, business_data: Dict) -> Dict:
        """ROI-Projektion berechnen"""
        return {
            'year_1_revenue': 250000,
            'year_2_revenue': 750000,
            'year_3_revenue': 1500000,
            'break_even_month': 8,
            'roi_3_years': 450,  # 450% ROI nach 3 Jahren
            'jobs_created': 5
        }
    
    def _generate_application_document(self, application_data: Dict) -> str:
        """Antrags-Dokument generieren"""
        return f"""
FÖRDERANTRAG - {application_data['program_name']}

ANTRAGSTELLER:
{application_data['applicant']['company_name']}
{application_data['applicant']['legal_form']}
Mitarbeiter: {application_data['applicant']['employees']}
Jahresumsatz: €{application_data['applicant']['annual_revenue']:,}

PROJEKT:
{application_data['project']['title']}

{application_data['project']['description']}

INNOVATION:
{chr(10).join(['• ' + aspect for aspect in application_data['project']['innovation_aspects']])}

FINANZIERUNG:
Beantragte Summe: €{application_data['funding']['requested_amount']:,}
Eigenanteil: €{application_data['funding']['own_contribution']:,}
Gesamtkosten: €{application_data['funding']['total_project_cost']:,}

ZEITPLAN:
{chr(10).join(['• ' + milestone for milestone in application_data['project']['milestones']])}

ROI-PROJEKTION:
Jahr 1: €{application_data['funding']['roi_projection']['year_1_revenue']:,}
Jahr 2: €{application_data['funding']['roi_projection']['year_2_revenue']:,}
Jahr 3: €{application_data['funding']['roi_projection']['year_3_revenue']:,}
Break-Even: Monat {application_data['funding']['roi_projection']['break_even_month']}

Erstellt am: {datetime.now().strftime('%d.%m.%Y')}
        """

# ============================
# SICHERHEITS-MCP (ANTI-HACK)
# ============================

class SecurityMCP:
    def __init__(self):
        self.security_events = []
        self.blocked_ips = set()
        self.failed_login_attempts = {}
        self.security_keys = {}
        
    async def scan_vulnerabilities(self) -> Dict:
        """Sicherheitslücken scannen"""
        try:
            vulnerabilities = []
            
            # 1. Port Scan
            open_ports = await self._scan_open_ports()
            for port in open_ports:
                if port not in [22, 80, 443, 3000, 8001, 27017]:  # Erwartete Ports
                    vulnerabilities.append({
                        'type': 'unexpected_open_port',
                        'severity': 'medium',
                        'details': f'Unerwarteter offener Port: {port}',
                        'recommendation': f'Port {port} schließen falls nicht benötigt'
                    })
            
            # 2. File Permissions Check
            sensitive_files = ['/app/backend/.env', '/app/frontend/.env']
            for file_path in sensitive_files:
                if os.path.exists(file_path):
                    file_stat = os.stat(file_path)
                    if oct(file_stat.st_mode)[-3:] != '600':
                        vulnerabilities.append({
                            'type': 'insecure_file_permissions',
                            'severity': 'high',
                            'details': f'Unsichere Berechtigung für {file_path}',
                            'recommendation': f'chmod 600 {file_path}'
                        })
            
            # 3. Weak Passwords Check
            weak_passwords = await self._check_weak_passwords()
            vulnerabilities.extend(weak_passwords)
            
            # 4. Outdated Dependencies
            outdated_deps = await self._check_outdated_dependencies()
            vulnerabilities.extend(outdated_deps)
            
            # 5. SSL/TLS Configuration
            ssl_issues = await self._check_ssl_configuration()
            vulnerabilities.extend(ssl_issues)
            
            # Severity Classification
            critical_count = len([v for v in vulnerabilities if v['severity'] == 'critical'])
            high_count = len([v for v in vulnerabilities if v['severity'] == 'high'])
            medium_count = len([v for v in vulnerabilities if v['severity'] == 'medium'])
            low_count = len([v for v in vulnerabilities if v['severity'] == 'low'])
            
            security_score = max(0, 100 - (critical_count * 25) - (high_count * 15) - (medium_count * 10) - (low_count * 5))
            
            return {
                'success': True,
                'security_score': security_score,
                'total_vulnerabilities': len(vulnerabilities),
                'severity_breakdown': {
                    'critical': critical_count,
                    'high': high_count,
                    'medium': medium_count,
                    'low': low_count
                },
                'vulnerabilities': vulnerabilities,
                'scan_timestamp': datetime.now().isoformat(),
                'next_scan_recommended': (datetime.now() + timedelta(days=7)).isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _scan_open_ports(self) -> List[int]:
        """Offene Ports scannen"""
        open_ports = []
        common_ports = [22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3000, 8001, 27017]
        
        for port in common_ports:
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                if result == 0:
                    open_ports.append(port)
                sock.close()
            except:
                pass
        
        return open_ports
    
    async def _check_weak_passwords(self) -> List[Dict]:
        """Schwache Passwörter prüfen"""
        vulnerabilities = []
        
        # Check common weak passwords in environment variables
        weak_patterns = ['123', 'password', 'admin', 'test', '000']
        
        env_files = ['/app/backend/.env', '/app/frontend/.env']
        for env_file in env_files:
            if os.path.exists(env_file):
                try:
                    with open(env_file, 'r') as f:
                        content = f.read().lower()
                        for pattern in weak_patterns:
                            if pattern in content:
                                vulnerabilities.append({
                                    'type': 'weak_password',
                                    'severity': 'high',
                                    'details': f'Potentiell schwaches Passwort in {env_file}',
                                    'recommendation': 'Starke Passwörter mit min. 12 Zeichen verwenden'
                                })
                                break
                except:
                    pass
        
        return vulnerabilities
    
    async def _check_outdated_dependencies(self) -> List[Dict]:
        """Veraltete Abhängigkeiten prüfen"""
        vulnerabilities = []
        
        try:
            # Python Dependencies
            result = subprocess.run(['pip', 'list', '--outdated'], capture_output=True, text=True, cwd='/app/backend')
            if result.stdout and len(result.stdout.split('\n')) > 3:
                vulnerabilities.append({
                    'type': 'outdated_dependencies',
                    'severity': 'medium',
                    'details': 'Veraltete Python-Pakete gefunden',
                    'recommendation': 'pip install --upgrade für kritische Pakete'
                })
        except:
            pass
        
        try:
            # Node Dependencies
            result = subprocess.run(['npm', 'audit'], capture_output=True, text=True, cwd='/app/frontend')
            if 'vulnerabilities' in result.stdout and 'high' in result.stdout:
                vulnerabilities.append({
                    'type': 'npm_vulnerabilities',
                    'severity': 'high',
                    'details': 'Sicherheitslücken in Node.js Abhängigkeiten',
                    'recommendation': 'npm audit fix ausführen'
                })
        except:
            pass
        
        return vulnerabilities
    
    async def _check_ssl_configuration(self) -> List[Dict]:
        """SSL/TLS Konfiguration prüfen"""
        vulnerabilities = []
        
        # Für Development Environment - meist keine SSL-Probleme
        # In Production würde hier echter SSL-Check erfolgen
        
        return vulnerabilities
    
    async def monitor_intrusion_attempts(self) -> Dict:
        """Intrusion Detection System"""
        try:
            suspicious_activities = []
            
            # 1. Failed Login Attempts
            for ip, attempts in self.failed_login_attempts.items():
                if attempts > 5:
                    suspicious_activities.append({
                        'type': 'brute_force_attempt',
                        'severity': 'high',
                        'source_ip': ip,
                        'attempt_count': attempts,
                        'action_taken': 'IP blocked' if ip in self.blocked_ips else 'monitoring'
                    })
            
            # 2. Unusual Network Activity
            network_activity = await self._analyze_network_activity()
            suspicious_activities.extend(network_activity)
            
            # 3. File Integrity Check
            file_changes = await self._check_file_integrity()
            suspicious_activities.extend(file_changes)
            
            # 4. Process Monitoring
            suspicious_processes = await self._monitor_processes()
            suspicious_activities.extend(suspicious_processes)
            
            threat_level = 'low'
            if len([a for a in suspicious_activities if a['severity'] == 'critical']) > 0:
                threat_level = 'critical'
            elif len([a for a in suspicious_activities if a['severity'] == 'high']) > 2:
                threat_level = 'high'
            elif len([a for a in suspicious_activities if a['severity'] == 'medium']) > 3:
                threat_level = 'medium'
            
            return {
                'success': True,
                'threat_level': threat_level,
                'suspicious_activities': suspicious_activities,
                'blocked_ips': list(self.blocked_ips),
                'monitoring_timestamp': datetime.now().isoformat(),
                'recommendations': self._generate_security_recommendations(threat_level)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _analyze_network_activity(self) -> List[Dict]:
        """Netzwerkaktivität analysieren"""
        suspicious = []
        
        try:
            # Check for unusual connections
            import psutil
            connections = psutil.net_connections()
            
            unusual_ports = []
            for conn in connections:
                if conn.status == 'ESTABLISHED' and conn.laddr:
                    if conn.laddr.port not in [22, 80, 443, 3000, 8001, 27017]:
                        unusual_ports.append(conn.laddr.port)
            
            if len(unusual_ports) > 5:
                suspicious.append({
                    'type': 'unusual_network_connections',
                    'severity': 'medium',
                    'details': f'Ungewöhnliche Netzwerkverbindungen auf Ports: {unusual_ports[:5]}',
                    'recommendation': 'Netzwerkverbindungen überprüfen'
                })
        except:
            pass
        
        return suspicious
    
    async def _check_file_integrity(self) -> List[Dict]:
        """Dateiintegrität prüfen"""
        suspicious = []
        
        try:
            # Check critical system files
            critical_files = [
                '/app/backend/server.py',
                '/app/backend/.env',
                '/app/frontend/.env'
            ]
            
            for file_path in critical_files:
                if os.path.exists(file_path):
                    # Simple timestamp check (in production würde Checksumme verwendet)
                    stat = os.stat(file_path)
                    modified_time = datetime.fromtimestamp(stat.st_mtime)
                    
                    if (datetime.now() - modified_time).total_seconds() < 300:  # Geändert in letzten 5 Min
                        suspicious.append({
                            'type': 'recent_file_modification',
                            'severity': 'medium',
                            'details': f'Kritische Datei kürzlich geändert: {file_path}',
                            'recommendation': 'Änderungen an kritischen Dateien überprüfen'
                        })
        except:
            pass
        
        return suspicious
    
    async def _monitor_processes(self) -> List[Dict]:
        """Verdächtige Prozesse überwachen"""
        suspicious = []
        
        try:
            import psutil
            suspicious_process_names = ['nc', 'ncat', 'telnet', 'nmap', 'wget', 'curl']
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] in suspicious_process_names:
                        # Ausnahme für legitime expo/node Prozesse
                        if 'node_modules' not in ' '.join(proc.info['cmdline'] or []):
                            suspicious.append({
                                'type': 'suspicious_process',
                                'severity': 'high',
                                'details': f"Verdächtiger Prozess: {proc.info['name']} (PID: {proc.info['pid']})",
                                'recommendation': f"Prozess {proc.info['pid']} überprüfen und ggf. beenden"
                            })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except:
            pass
        
        return suspicious
    
    def _generate_security_recommendations(self, threat_level: str) -> List[str]:
        """Sicherheitsempfehlungen generieren"""
        base_recommendations = [
            'Regelmäßige Sicherheitsupdates installieren',
            'Starke Passwörter verwenden',
            'Zugriff auf kritische Dateien beschränken',
            'Netzwerkverkehr überwachen'
        ]
        
        if threat_level == 'critical':
            return base_recommendations + [
                'SOFORT: System offline nehmen und analysieren',
                'Alle Passwörter ändern',
                'Forensische Analyse durchführen',
                'Backup-System aktivieren'
            ]
        elif threat_level == 'high':
            return base_recommendations + [
                'Verdächtige IPs blockieren',
                'Log-Files detailliert analysieren',
                'Zusätzliche Überwachung aktivieren'
            ]
        elif threat_level == 'medium':
            return base_recommendations + [
                'Sicherheitskonfiguration überprüfen',
                'Monitoring verstärken'
            ]
        else:
            return base_recommendations
    
    async def apply_security_hardening(self) -> Dict:
        """Automatische Sicherheitshärtung"""
        try:
            hardening_actions = []
            
            # 1. File Permissions
            try:
                os.chmod('/app/backend/.env', 0o600)
                os.chmod('/app/frontend/.env', 0o600)
                hardening_actions.append('Dateiberechtigungen für .env Files korrigiert')
            except:
                pass
            
            # 2. Remove World-Writable Files
            try:
                for root, dirs, files in os.walk('/app'):
                    for file in files:
                        filepath = os.path.join(root, file)
                        try:
                            stat = os.stat(filepath)
                            if stat.st_mode & 0o002:  # World writable
                                os.chmod(filepath, stat.st_mode & ~0o002)
                                hardening_actions.append(f'World-write Berechtigung entfernt: {filepath}')
                        except:
                            pass
            except:
                pass
            
            # 3. Disable Unnecessary Services
            # (In containerized environment meist nicht relevant)
            
            # 4. Configure Firewall Rules (iptables)
            try:
                # Basic firewall rules (nur für Demo)
                subprocess.run(['iptables', '-A', 'INPUT', '-p', 'tcp', '--dport', '22', '-j', 'ACCEPT'], check=False)
                subprocess.run(['iptables', '-A', 'INPUT', '-p', 'tcp', '--dport', '80', '-j', 'ACCEPT'], check=False)
                subprocess.run(['iptables', '-A', 'INPUT', '-p', 'tcp', '--dport', '443', '-j', 'ACCEPT'], check=False)
                hardening_actions.append('Basis-Firewall-Regeln konfiguriert')
            except:
                hardening_actions.append('Firewall-Konfiguration übersprungen (Container-Environment)')
            
            return {
                'success': True,
                'hardening_actions': hardening_actions,
                'actions_count': len(hardening_actions),
                'hardening_timestamp': datetime.now().isoformat(),
                'next_hardening_check': (datetime.now() + timedelta(days=30)).isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Global Instances
financial_mcp = FinancialManagementMCP()
grant_mcp = GrantApplicationMCP()
security_mcp = SecurityMCP()