#!/usr/bin/env python3
"""
Backend API Testing for LeadMaps Application
Tests the complete integrated LeadMaps system with new backend API endpoints
"""

import requests
import json
import time
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://workflow-automation-5.preview.emergentagent.com')
API_BASE_URL = f"{BACKEND_URL}/api"

class BackendTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_data = {
            'search_ids': [],
            'lead_ids': [],
            'sample_leads': []
        }
        
    def log_test(self, test_name, status, message, response_data=None):
        """Log test results"""
        self.total_tests += 1
        if status == "PASS":
            self.passed_tests += 1
        else:
            self.failed_tests += 1
            
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        print(f"[{status}] {test_name}: {message}")
        
    def test_root_endpoint(self):
        """Test GET /api/ endpoint"""
        try:
            response = requests.get(f"{API_BASE_URL}/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("message") == "Hello World":
                    self.log_test("Root Endpoint", "PASS", "Root endpoint returns correct message", data)
                else:
                    self.log_test("Root Endpoint", "FAIL", f"Unexpected response: {data}", data)
            else:
                self.log_test("Root Endpoint", "FAIL", f"HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Root Endpoint", "FAIL", f"Request failed: {str(e)}")
            
    def test_create_status_check(self):
        """Test POST /api/status endpoint"""
        try:
            test_data = {
                "client_name": "LeadMaps Test Client"
            }
            
            response = requests.post(
                f"{API_BASE_URL}/status", 
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["id", "client_name", "timestamp"]
                
                if all(field in data for field in required_fields):
                    if data["client_name"] == test_data["client_name"]:
                        self.log_test("Create Status Check", "PASS", "Status check created successfully", data)
                        return data["id"]  # Return ID for further testing
                    else:
                        self.log_test("Create Status Check", "FAIL", "Client name mismatch in response", data)
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_test("Create Status Check", "FAIL", f"Missing fields: {missing_fields}", data)
            else:
                self.log_test("Create Status Check", "FAIL", f"HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Create Status Check", "FAIL", f"Request failed: {str(e)}")
            
        return None
        
    def test_get_status_checks(self):
        """Test GET /api/status endpoint"""
        try:
            response = requests.get(f"{API_BASE_URL}/status", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    self.log_test("Get Status Checks", "PASS", f"Retrieved {len(data)} status checks", {"count": len(data)})
                    
                    # Validate structure of first item if exists
                    if len(data) > 0:
                        first_item = data[0]
                        required_fields = ["id", "client_name", "timestamp"]
                        if all(field in first_item for field in required_fields):
                            self.log_test("Status Check Structure", "PASS", "Status check structure is valid", first_item)
                        else:
                            missing_fields = [field for field in required_fields if field not in first_item]
                            self.log_test("Status Check Structure", "FAIL", f"Missing fields: {missing_fields}", first_item)
                else:
                    self.log_test("Get Status Checks", "FAIL", "Response is not a list", data)
            else:
                self.log_test("Get Status Checks", "FAIL", f"HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Get Status Checks", "FAIL", f"Request failed: {str(e)}")
            
    def test_cors_headers(self):
        """Test CORS configuration"""
        try:
            response = requests.options(f"{API_BASE_URL}/", timeout=10)
            
            cors_headers = {
                "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
            }
            
            if cors_headers["Access-Control-Allow-Origin"]:
                self.log_test("CORS Configuration", "PASS", "CORS headers present", cors_headers)
            else:
                self.log_test("CORS Configuration", "FAIL", "CORS headers missing", cors_headers)
                
        except requests.exceptions.RequestException as e:
            self.log_test("CORS Configuration", "FAIL", f"Request failed: {str(e)}")
            
    def test_invalid_endpoints(self):
        """Test non-existent endpoints return appropriate errors"""
        try:
            response = requests.get(f"{API_BASE_URL}/nonexistent", timeout=10)
            
            if response.status_code == 404:
                self.log_test("Invalid Endpoint Handling", "PASS", "404 returned for non-existent endpoint")
            else:
                self.log_test("Invalid Endpoint Handling", "FAIL", f"Expected 404, got {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Invalid Endpoint Handling", "FAIL", f"Request failed: {str(e)}")
            
    def test_malformed_requests(self):
        """Test API handles malformed requests properly"""
        try:
            # Test POST with invalid JSON
            response = requests.post(
                f"{API_BASE_URL}/status",
                data="invalid json",
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code in [400, 422]:  # Bad Request or Unprocessable Entity
                self.log_test("Malformed Request Handling", "PASS", f"Properly handled malformed JSON (HTTP {response.status_code})")
            else:
                self.log_test("Malformed Request Handling", "FAIL", f"Unexpected status code: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Malformed Request Handling", "FAIL", f"Request failed: {str(e)}")
            
    def test_missing_required_fields(self):
        """Test API validation for missing required fields"""
        try:
            # Test POST without required client_name field
            response = requests.post(
                f"{API_BASE_URL}/status",
                json={},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 422:  # Unprocessable Entity (validation error)
                self.log_test("Required Field Validation", "PASS", "Properly validates missing required fields")
            else:
                self.log_test("Required Field Validation", "FAIL", f"Expected 422, got {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Required Field Validation", "FAIL", f"Request failed: {str(e)}")
            
    def test_lead_scraping_api(self):
        """Test POST /api/leads/scrape - Lead scraping functionality"""
        try:
            # Test with realistic search parameters
            search_data = {
                "query": "restaurants",
                "city": "New York",
                "state": "NY",
                "zipCode": "10001",
                "maxResults": 15
            }
            
            start_time = time.time()
            response = requests.post(
                f"{API_BASE_URL}/leads/scrape",
                json=search_data,
                headers={"Content-Type": "application/json"},
                timeout=30  # Allow for realistic delay
            )
            end_time = time.time()
            processing_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["searchId", "results", "count", "message"]
                
                if all(field in data for field in required_fields):
                    # Validate realistic delay (2-4 seconds)
                    if 2 <= processing_time <= 6:  # Allow some buffer
                        self.log_test("Lead Scraping API - Timing", "PASS", f"Realistic delay: {processing_time:.2f}s")
                    else:
                        self.log_test("Lead Scraping API - Timing", "FAIL", f"Unrealistic delay: {processing_time:.2f}s (expected 2-4s)")
                    
                    # Validate lead data structure
                    if data["count"] > 0 and len(data["results"]) > 0:
                        lead = data["results"][0]
                        lead_fields = ["id", "businessName", "businessType", "address", "searchId"]
                        
                        if all(field in lead for field in lead_fields):
                            # Store test data for further testing
                            self.test_data['search_ids'].append(data["searchId"])
                            self.test_data['lead_ids'].extend([lead["id"] for lead in data["results"]])
                            self.test_data['sample_leads'] = data["results"][:3]  # Store first 3 leads
                            
                            self.log_test("Lead Scraping API", "PASS", 
                                        f"Successfully scraped {data['count']} leads with proper structure", 
                                        {"searchId": data["searchId"], "count": data["count"]})
                        else:
                            missing_fields = [field for field in lead_fields if field not in lead]
                            self.log_test("Lead Scraping API", "FAIL", f"Lead missing fields: {missing_fields}", lead)
                    else:
                        self.log_test("Lead Scraping API", "FAIL", "No leads returned", data)
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_test("Lead Scraping API", "FAIL", f"Response missing fields: {missing_fields}", data)
            else:
                self.log_test("Lead Scraping API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Lead Scraping API", "FAIL", f"Request failed: {str(e)}")
    
    def test_lead_scraping_variations(self):
        """Test lead scraping with different parameters"""
        test_cases = [
            {
                "name": "Different City/State",
                "data": {"query": "coffee shops", "city": "Los Angeles", "state": "CA", "maxResults": 10}
            },
            {
                "name": "With Zip Code",
                "data": {"query": "plumbers", "city": "Austin", "state": "TX", "zipCode": "78701", "maxResults": 5}
            },
            {
                "name": "Max Results Limit",
                "data": {"query": "gyms", "city": "Miami", "state": "FL", "maxResults": 25}
            }
        ]
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{API_BASE_URL}/leads/scrape",
                    json=test_case["data"],
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data["count"] <= test_case["data"]["maxResults"]:
                        self.test_data['search_ids'].append(data["searchId"])
                        self.log_test(f"Lead Scraping - {test_case['name']}", "PASS", 
                                    f"Returned {data['count']} leads (≤ {test_case['data']['maxResults']})")
                    else:
                        self.log_test(f"Lead Scraping - {test_case['name']}", "FAIL", 
                                    f"Returned {data['count']} leads (> {test_case['data']['maxResults']})")
                else:
                    self.log_test(f"Lead Scraping - {test_case['name']}", "FAIL", 
                                f"HTTP {response.status_code}: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                self.log_test(f"Lead Scraping - {test_case['name']}", "FAIL", f"Request failed: {str(e)}")
    
    def test_email_enrichment_api(self):
        """Test POST /api/leads/enrich-email - Email enrichment functionality"""
        if not self.test_data['sample_leads']:
            self.log_test("Email Enrichment API", "SKIP", "No sample leads available for testing")
            return
            
        try:
            # Test with a lead that has a website
            test_lead = None
            for lead in self.test_data['sample_leads']:
                if lead.get('website'):
                    test_lead = lead
                    break
            
            if not test_lead:
                self.log_test("Email Enrichment API", "SKIP", "No leads with websites available for testing")
                return
            
            enrichment_data = {
                "leadId": test_lead["id"],
                "website": test_lead["website"]
            }
            
            response = requests.post(
                f"{API_BASE_URL}/leads/enrich-email",
                json=enrichment_data,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["success", "email", "message"]
                
                if all(field in data for field in required_fields):
                    if data["success"] and data["email"]:
                        # Validate email format
                        email = data["email"]
                        if "@" in email and "." in email:
                            self.log_test("Email Enrichment API", "PASS", 
                                        f"Successfully enriched email: {email}", data)
                        else:
                            self.log_test("Email Enrichment API", "FAIL", 
                                        f"Invalid email format: {email}", data)
                    else:
                        self.log_test("Email Enrichment API", "PASS", 
                                    "Email enrichment completed (no email found)", data)
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_test("Email Enrichment API", "FAIL", f"Response missing fields: {missing_fields}", data)
            else:
                self.log_test("Email Enrichment API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Email Enrichment API", "FAIL", f"Request failed: {str(e)}")
    
    def test_email_enrichment_error_handling(self):
        """Test email enrichment error handling"""
        test_cases = [
            {
                "name": "Invalid Lead ID",
                "data": {"leadId": "invalid-lead-id", "website": "https://example.com"},
                "expected_status": 404
            },
            {
                "name": "Missing Website",
                "data": {"leadId": self.test_data['lead_ids'][0] if self.test_data['lead_ids'] else "test-id"},
                "expected_status": 422
            }
        ]
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{API_BASE_URL}/leads/enrich-email",
                    json=test_case["data"],
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == test_case["expected_status"]:
                    self.log_test(f"Email Enrichment - {test_case['name']}", "PASS", 
                                f"Proper error handling (HTTP {response.status_code})")
                else:
                    self.log_test(f"Email Enrichment - {test_case['name']}", "FAIL", 
                                f"Expected HTTP {test_case['expected_status']}, got {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                self.log_test(f"Email Enrichment - {test_case['name']}", "FAIL", f"Request failed: {str(e)}")
    
    def test_dashboard_stats_api(self):
        """Test GET /api/leads/dashboard/stats - Dashboard analytics"""
        try:
            response = requests.get(f"{API_BASE_URL}/leads/dashboard/stats", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["totalLeads", "totalSearches", "avgConversion", "emailsEnriched", "recentSearches"]
                
                if all(field in data for field in required_fields):
                    # Validate data types and ranges
                    validations = [
                        (isinstance(data["totalLeads"], int) and data["totalLeads"] >= 0, "totalLeads should be non-negative integer"),
                        (isinstance(data["totalSearches"], int) and data["totalSearches"] >= 0, "totalSearches should be non-negative integer"),
                        (isinstance(data["avgConversion"], (int, float)) and 0 <= data["avgConversion"] <= 100, "avgConversion should be 0-100"),
                        (isinstance(data["emailsEnriched"], int) and data["emailsEnriched"] >= 0, "emailsEnriched should be non-negative integer"),
                        (isinstance(data["recentSearches"], list), "recentSearches should be a list")
                    ]
                    
                    all_valid = True
                    for is_valid, message in validations:
                        if not is_valid:
                            self.log_test("Dashboard Stats API - Validation", "FAIL", message, data)
                            all_valid = False
                    
                    if all_valid:
                        # Validate recent searches structure
                        if data["recentSearches"]:
                            search = data["recentSearches"][0]
                            search_fields = ["id", "query", "results", "date"]
                            if all(field in search for field in search_fields):
                                self.log_test("Dashboard Stats API", "PASS", 
                                            f"Dashboard stats retrieved successfully", 
                                            {k: v for k, v in data.items() if k != "recentSearches"})
                            else:
                                missing_fields = [field for field in search_fields if field not in search]
                                self.log_test("Dashboard Stats API", "FAIL", 
                                            f"Recent search missing fields: {missing_fields}", search)
                        else:
                            self.log_test("Dashboard Stats API", "PASS", 
                                        "Dashboard stats retrieved (no recent searches)", data)
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_test("Dashboard Stats API", "FAIL", f"Response missing fields: {missing_fields}", data)
            else:
                self.log_test("Dashboard Stats API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Dashboard Stats API", "FAIL", f"Request failed: {str(e)}")
    
    def test_search_results_api(self):
        """Test GET /api/leads/search/{search_id} - Individual search retrieval"""
        if not self.test_data['search_ids']:
            self.log_test("Search Results API", "SKIP", "No search IDs available for testing")
            return
            
        try:
            search_id = self.test_data['search_ids'][0]
            response = requests.get(f"{API_BASE_URL}/leads/search/{search_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["search", "leads", "count"]
                
                if all(field in data for field in required_fields):
                    # Validate search record structure
                    search = data["search"]
                    search_fields = ["id", "query", "city", "state", "maxResults"]
                    
                    if all(field in search for field in search_fields):
                        # Validate leads data
                        if data["count"] == len(data["leads"]):
                            self.log_test("Search Results API", "PASS", 
                                        f"Retrieved search with {data['count']} leads", 
                                        {"searchId": search_id, "count": data["count"]})
                        else:
                            self.log_test("Search Results API", "FAIL", 
                                        f"Count mismatch: reported {data['count']}, actual {len(data['leads'])}")
                    else:
                        missing_fields = [field for field in search_fields if field not in search]
                        self.log_test("Search Results API", "FAIL", f"Search record missing fields: {missing_fields}", search)
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_test("Search Results API", "FAIL", f"Response missing fields: {missing_fields}", data)
            else:
                self.log_test("Search Results API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Search Results API", "FAIL", f"Request failed: {str(e)}")
    
    def test_search_results_error_handling(self):
        """Test search results error handling for non-existent searches"""
        try:
            fake_search_id = "non-existent-search-id"
            response = requests.get(f"{API_BASE_URL}/leads/search/{fake_search_id}", timeout=10)
            
            if response.status_code == 404:
                self.log_test("Search Results - Error Handling", "PASS", "Proper 404 for non-existent search")
            else:
                self.log_test("Search Results - Error Handling", "FAIL", 
                            f"Expected 404, got {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Search Results - Error Handling", "FAIL", f"Request failed: {str(e)}")
    
    def test_csv_export_api(self):
        """Test GET /api/leads/export/{search_id} - CSV export functionality"""
        if not self.test_data['search_ids']:
            self.log_test("CSV Export API", "SKIP", "No search IDs available for testing")
            return
            
        try:
            search_id = self.test_data['search_ids'][0]
            response = requests.get(f"{API_BASE_URL}/leads/export/{search_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["csv_content", "filename", "count"]
                
                if all(field in data for field in required_fields):
                    # Validate CSV content
                    csv_content = data["csv_content"]
                    lines = csv_content.split('\n')
                    
                    if len(lines) > 1:  # Header + at least one data row
                        # Check header
                        expected_headers = ["Business Name", "Type", "Address", "Phone", "Website", "Email", "Rating", "Reviews", "Search Query"]
                        header_line = lines[0]
                        
                        headers_present = all(header in header_line for header in expected_headers[:5])  # Check first 5 critical headers
                        
                        if headers_present:
                            # Validate filename format
                            filename = data["filename"]
                            if filename.endswith('.csv') and 'leads_' in filename:
                                self.log_test("CSV Export API", "PASS", 
                                            f"CSV export successful: {data['count']} leads, filename: {filename}")
                            else:
                                self.log_test("CSV Export API", "FAIL", f"Invalid filename format: {filename}")
                        else:
                            self.log_test("CSV Export API", "FAIL", "CSV missing required headers")
                    else:
                        self.log_test("CSV Export API", "FAIL", "CSV content appears empty or invalid")
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_test("CSV Export API", "FAIL", f"Response missing fields: {missing_fields}", data)
            else:
                self.log_test("CSV Export API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("CSV Export API", "FAIL", f"Request failed: {str(e)}")
    
    def test_csv_export_error_handling(self):
        """Test CSV export error handling"""
        try:
            fake_search_id = "non-existent-search-id"
            response = requests.get(f"{API_BASE_URL}/leads/export/{fake_search_id}", timeout=10)
            
            if response.status_code == 404:
                self.log_test("CSV Export - Error Handling", "PASS", "Proper 404 for non-existent search")
            else:
                self.log_test("CSV Export - Error Handling", "FAIL", 
                            f"Expected 404, got {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("CSV Export - Error Handling", "FAIL", f"Request failed: {str(e)}")
    
    def test_database_integration(self):
        """Test database integration and data persistence"""
        if not self.test_data['search_ids']:
            self.log_test("Database Integration", "SKIP", "No test data available")
            return
            
        try:
            # Test that search persists and can be retrieved
            search_id = self.test_data['search_ids'][0]
            
            # Get search results
            response = requests.get(f"{API_BASE_URL}/leads/search/{search_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify UUID format for search ID
                if len(search_id.split('-')) == 5:  # UUID format
                    # Verify timestamp exists and is recent
                    search = data["search"]
                    if "created_at" in search:
                        self.log_test("Database Integration - UUID & Timestamps", "PASS", 
                                    "Proper UUID generation and timestamp handling")
                    else:
                        self.log_test("Database Integration - UUID & Timestamps", "FAIL", 
                                    "Missing timestamp in search record")
                        
                    # Verify lead associations
                    leads = data["leads"]
                    if leads and all(lead.get("searchId") == search_id for lead in leads):
                        self.log_test("Database Integration - Relationships", "PASS", 
                                    "Proper lead-search relationships maintained")
                    else:
                        self.log_test("Database Integration - Relationships", "FAIL", 
                                    "Lead-search relationship issues")
                else:
                    self.log_test("Database Integration - UUID & Timestamps", "FAIL", 
                                f"Invalid UUID format: {search_id}")
            else:
                self.log_test("Database Integration", "FAIL", 
                            f"Failed to retrieve persisted data: HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Database Integration", "FAIL", f"Request failed: {str(e)}")
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow: scrape → store → retrieve → enrich → export"""
        try:
            # Step 1: Scrape leads
            search_data = {
                "query": "coffee shops",
                "city": "Seattle",
                "state": "WA",
                "maxResults": 8
            }
            
            scrape_response = requests.post(
                f"{API_BASE_URL}/leads/scrape",
                json=search_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if scrape_response.status_code != 200:
                self.log_test("End-to-End Workflow", "FAIL", "Step 1 (Scrape) failed")
                return
                
            scrape_data = scrape_response.json()
            search_id = scrape_data["searchId"]
            
            # Step 2: Retrieve stored data
            time.sleep(1)  # Brief pause
            retrieve_response = requests.get(f"{API_BASE_URL}/leads/search/{search_id}", timeout=10)
            
            if retrieve_response.status_code != 200:
                self.log_test("End-to-End Workflow", "FAIL", "Step 2 (Retrieve) failed")
                return
                
            retrieve_data = retrieve_response.json()
            
            # Step 3: Enrich email (if possible)
            leads_with_websites = [lead for lead in retrieve_data["leads"] if lead.get("website")]
            if leads_with_websites:
                enrich_data = {
                    "leadId": leads_with_websites[0]["id"],
                    "website": leads_with_websites[0]["website"]
                }
                
                enrich_response = requests.post(
                    f"{API_BASE_URL}/leads/enrich-email",
                    json=enrich_data,
                    headers={"Content-Type": "application/json"},
                    timeout=15
                )
                
                enrich_success = enrich_response.status_code == 200
            else:
                enrich_success = True  # Skip if no websites available
            
            # Step 4: Export CSV
            export_response = requests.get(f"{API_BASE_URL}/leads/export/{search_id}", timeout=10)
            
            if export_response.status_code == 200 and enrich_success:
                self.log_test("End-to-End Workflow", "PASS", 
                            f"Complete workflow successful: scrape → store → retrieve → enrich → export")
            else:
                self.log_test("End-to-End Workflow", "FAIL", 
                            f"Workflow failed at export step (HTTP {export_response.status_code})")
                
        except requests.exceptions.RequestException as e:
            self.log_test("End-to-End Workflow", "FAIL", f"Workflow failed: {str(e)}")
    
    def run_leadmaps_tests(self):
        """Run all LeadMaps-specific API tests"""
        print(f"\n{'='*60}")
        print("LEADMAPS LEAD SCRAPING API TESTING")
        print(f"Testing API at: {API_BASE_URL}")
        print(f"{'='*60}\n")
        
        # Lead Scraping API Tests
        print("🔍 Testing Lead Scraping API...")
        self.test_lead_scraping_api()
        self.test_lead_scraping_variations()
        
        # Email Enrichment API Tests  
        print("\n📧 Testing Email Enrichment API...")
        self.test_email_enrichment_api()
        self.test_email_enrichment_error_handling()
        
        # Dashboard Stats API Tests
        print("\n📊 Testing Dashboard Stats API...")
        self.test_dashboard_stats_api()
        
        # Search Results API Tests
        print("\n🔎 Testing Search Results API...")
        self.test_search_results_api()
        self.test_search_results_error_handling()
        
        # CSV Export API Tests
        print("\n📄 Testing CSV Export API...")
        self.test_csv_export_api()
        self.test_csv_export_error_handling()
        
        # Database Integration Tests
        print("\n🗄️ Testing Database Integration...")
        self.test_database_integration()
        
        # End-to-End Workflow Test
        print("\n🔄 Testing End-to-End Workflow...")
        self.test_end_to_end_workflow()
        
        return self.get_summary()
        
    def get_summary(self):
        """Get test summary"""
        return {
            "total": self.total_tests,
            "passed": self.passed_tests,
            "failed": self.failed_tests,
            "success_rate": (self.passed_tests/self.total_tests)*100 if self.total_tests > 0 else 0,
            "results": self.test_results
        }
            
    def run_all_tests(self):
        """Run all backend tests including basic API and LeadMaps functionality"""
        print(f"\n{'='*60}")
        print("LEADMAPS BACKEND API TESTING")
        print(f"Testing API at: {API_BASE_URL}")
        print(f"{'='*60}\n")
        
        # Basic API functionality tests (existing)
        print("🔧 Testing Basic API Functionality...")
        self.test_root_endpoint()
        self.test_create_status_check()
        self.test_get_status_checks()
        
        # Configuration and error handling tests (existing)
        print("\n⚙️ Testing Configuration & Error Handling...")
        self.test_cors_headers()
        self.test_invalid_endpoints()
        self.test_malformed_requests()
        self.test_missing_required_fields()
        
        # Data persistence test (existing)
        print("\n🗄️ Testing Basic Data Persistence...")
        self.test_data_persistence()
        
        # LeadMaps-specific tests (new)
        print(f"\n{'='*60}")
        print("LEADMAPS LEAD SCRAPING SYSTEM TESTING")
        print(f"{'='*60}")
        
        leadmaps_summary = self.run_leadmaps_tests()
        
        # Print comprehensive summary
        print(f"\n{'='*60}")
        print("COMPREHENSIVE TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        
        if self.failed_tests > 0:
            print(f"\nFAILED TESTS:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"- {result['test']}: {result['message']}")
        
        print(f"\n{'='*60}\n")
        
        return {
            "total": self.total_tests,
            "passed": self.passed_tests,
            "failed": self.failed_tests,
            "success_rate": (self.passed_tests/self.total_tests)*100,
            "results": self.test_results
        }
    
    def test_data_persistence(self):
        """Test that data persists in MongoDB"""
        try:
            # Create a status check
            test_data = {"client_name": "Persistence Test Client"}
            create_response = requests.post(
                f"{API_BASE_URL}/status",
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if create_response.status_code == 200:
                created_id = create_response.json().get("id")
                
                # Wait a moment then retrieve all status checks
                time.sleep(1)
                get_response = requests.get(f"{API_BASE_URL}/status", timeout=10)
                
                if get_response.status_code == 200:
                    all_checks = get_response.json()
                    
                    # Check if our created item exists
                    found_item = None
                    for check in all_checks:
                        if check.get("id") == created_id:
                            found_item = check
                            break
                            
                    if found_item:
                        self.log_test("Data Persistence", "PASS", "Data persists correctly in database", found_item)
                    else:
                        self.log_test("Data Persistence", "FAIL", "Created item not found in database")
                else:
                    self.log_test("Data Persistence", "FAIL", f"Failed to retrieve data: HTTP {get_response.status_code}")
            else:
                self.log_test("Data Persistence", "FAIL", f"Failed to create test data: HTTP {create_response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Data Persistence", "FAIL", f"Request failed: {str(e)}")

if __name__ == "__main__":
    tester = BackendTester()
    results = tester.run_all_tests()
    
    # Save results to file
    with open("/app/backend_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Detailed results saved to: /app/backend_test_results.json")