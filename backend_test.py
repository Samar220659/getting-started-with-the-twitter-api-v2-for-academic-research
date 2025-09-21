#!/usr/bin/env python3
"""
Backend API Testing for LeadMaps Application
Tests the existing FastAPI endpoints and MongoDB integration
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
            
    def run_all_tests(self):
        """Run all backend tests"""
        print(f"\n{'='*60}")
        print("LEADMAPS BACKEND API TESTING")
        print(f"Testing API at: {API_BASE_URL}")
        print(f"{'='*60}\n")
        
        # Core API functionality tests
        self.test_root_endpoint()
        self.test_create_status_check()
        self.test_get_status_checks()
        
        # Configuration and error handling tests
        self.test_cors_headers()
        self.test_invalid_endpoints()
        self.test_malformed_requests()
        self.test_missing_required_fields()
        
        # Data persistence test
        self.test_data_persistence()
        
        # Print summary
        print(f"\n{'='*60}")
        print("TEST SUMMARY")
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

if __name__ == "__main__":
    tester = BackendTester()
    results = tester.run_all_tests()
    
    # Save results to file
    with open("/app/backend_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Detailed results saved to: /app/backend_test_results.json")