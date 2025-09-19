#!/usr/bin/env python3
"""
Comprehensive Backend Test Suite for ZZ-LOBBY-BOOST Automation System
Tests all major functionalities including workflow management, lead management,
content generation, social media management, revenue tracking, and automation.
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
import uuid

class ZZLobbyBoostTester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api"
        self.session = requests.Session()
        self.test_data = {}
        
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """Make HTTP request and return response"""
        url = f"{self.api_url}{endpoint}"
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, params=params)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, params=params)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            self.log(f"{method} {url} -> {response.status_code}")
            
            if response.status_code >= 400:
                self.log(f"Error response: {response.text}", "ERROR")
                
            return {
                "status_code": response.status_code,
                "data": response.json() if response.content else {},
                "success": 200 <= response.status_code < 300
            }
        except Exception as e:
            self.log(f"Request failed: {str(e)}", "ERROR")
            return {"status_code": 0, "data": {}, "success": False, "error": str(e)}

    def test_api_health(self) -> bool:
        """Test if API is accessible"""
        self.log("=== Testing API Health ===")
        result = self.make_request("GET", "/")
        
        if result["success"]:
            self.log("✅ API is accessible and responding")
            return True
        else:
            self.log("❌ API health check failed", "ERROR")
            return False

    def test_workflow_management(self) -> bool:
        """Test workflow CRUD operations"""
        self.log("=== Testing Workflow Management ===")
        success = True
        
        # 1. Create workflow
        workflow_data = {
            "name": "Test Marketing Automation",
            "description": "Automatisierter Marketing-Workflow für Lead-Generierung und Content-Erstellung",
            "type": "lead_gen",
            "config": {
                "target_audience": "Deutsche Unternehmen",
                "content_types": ["video_script", "social_post", "email"],
                "platforms": ["youtube", "linkedin", "tiktok"]
            }
        }
        
        result = self.make_request("POST", "/workflows", workflow_data)
        if result["success"]:
            self.test_data["workflow_id"] = result["data"]["id"]
            self.log("✅ Workflow creation successful")
        else:
            self.log("❌ Workflow creation failed", "ERROR")
            success = False
            
        # 2. Get all workflows
        result = self.make_request("GET", "/workflows")
        if result["success"] and len(result["data"]) > 0:
            self.log("✅ Workflow retrieval successful")
        else:
            self.log("❌ Workflow retrieval failed", "ERROR")
            success = False
            
        # 3. Get specific workflow
        if "workflow_id" in self.test_data:
            result = self.make_request("GET", f"/workflows/{self.test_data['workflow_id']}")
            if result["success"]:
                self.log("✅ Specific workflow retrieval successful")
            else:
                self.log("❌ Specific workflow retrieval failed", "ERROR")
                success = False
                
        # 4. Update workflow status
        if "workflow_id" in self.test_data:
            result = self.make_request("PUT", f"/workflows/{self.test_data['workflow_id']}/status", 
                                     params={"status": "active"})
            if result["success"]:
                self.log("✅ Workflow status update successful")
            else:
                self.log("❌ Workflow status update failed", "ERROR")
                success = False
                
        return success

    def test_lead_management(self) -> bool:
        """Test lead CRUD operations and scoring"""
        self.log("=== Testing Lead Management ===")
        success = True
        
        if "workflow_id" not in self.test_data:
            self.log("❌ No workflow available for lead testing", "ERROR")
            return False
            
        # 1. Create lead
        lead_data = {
            "email": "max.mueller@techfirma.de",
            "company": "TechFirma GmbH",
            "industry": "Software Development",
            "pain_points": ["Zeitaufwändige manuelle Prozesse", "Ineffiziente Lead-Generierung", "Fehlende Automatisierung"],
            "source": "website",
            "workflow_id": self.test_data["workflow_id"]
        }
        
        result = self.make_request("POST", "/leads", lead_data)
        if result["success"]:
            self.test_data["lead_id"] = result["data"]["id"]
            self.log("✅ Lead creation successful")
        else:
            self.log("❌ Lead creation failed", "ERROR")
            success = False
            
        # 2. Get all leads
        result = self.make_request("GET", "/leads")
        if result["success"]:
            self.log("✅ Lead retrieval successful")
        else:
            self.log("❌ Lead retrieval failed", "ERROR")
            success = False
            
        # 3. Get leads by workflow
        result = self.make_request("GET", "/leads", params={"workflow_id": self.test_data["workflow_id"]})
        if result["success"]:
            self.log("✅ Lead retrieval by workflow successful")
        else:
            self.log("❌ Lead retrieval by workflow failed", "ERROR")
            success = False
            
        # 4. Update lead score
        if "lead_id" in self.test_data:
            result = self.make_request("PUT", f"/leads/{self.test_data['lead_id']}/score", 
                                     params={"score": 8})
            if result["success"]:
                self.log("✅ Lead score update successful")
            else:
                self.log("❌ Lead score update failed", "ERROR")
                success = False
                
        return success

    def test_content_generation(self) -> bool:
        """Test LLM-powered content generation"""
        self.log("=== Testing Content Generation (LLM Integration) ===")
        success = True
        
        if "workflow_id" not in self.test_data:
            self.log("❌ No workflow available for content testing", "ERROR")
            return False
            
        content_types = ["video_script", "social_post", "email", "blog"]
        
        for content_type in content_types:
            self.log(f"Testing {content_type} generation...")
            
            content_data = {
                "content_type": content_type,
                "target_audience": "Deutsche Unternehmer und Marketing-Manager",
                "keywords": ["Automatisierung", "Effizienz", "Lead-Generierung", "Content-Marketing"],
                "workflow_id": self.test_data["workflow_id"],
                "lead_id": self.test_data.get("lead_id")
            }
            
            result = self.make_request("POST", "/content/generate", content_data)
            if result["success"]:
                if content_type == "video_script":
                    self.test_data["content_id"] = result["data"]["id"]
                self.log(f"✅ {content_type} generation successful")
                
                # Verify content has German text
                content_text = result["data"].get("content", "")
                if any(word in content_text.lower() for word in ["der", "die", "das", "und", "für", "mit"]):
                    self.log(f"✅ {content_type} contains German content")
                else:
                    self.log(f"⚠️ {content_type} may not be in German", "WARNING")
            else:
                self.log(f"❌ {content_type} generation failed", "ERROR")
                success = False
                
        # Test content retrieval
        result = self.make_request("GET", "/content")
        if result["success"]:
            self.log("✅ Content retrieval successful")
        else:
            self.log("❌ Content retrieval failed", "ERROR")
            success = False
            
        # Test content retrieval by workflow
        result = self.make_request("GET", "/content", params={"workflow_id": self.test_data["workflow_id"]})
        if result["success"]:
            self.log("✅ Content retrieval by workflow successful")
        else:
            self.log("❌ Content retrieval by workflow failed", "ERROR")
            success = False
            
        return success

    def test_social_media_management(self) -> bool:
        """Test social media post scheduling and management"""
        self.log("=== Testing Social Media Management ===")
        success = True
        
        if "content_id" not in self.test_data:
            self.log("❌ No content available for social media testing", "ERROR")
            return False
            
        platforms = ["youtube", "tiktok", "instagram", "linkedin"]
        
        for platform in platforms:
            self.log(f"Testing {platform} post scheduling...")
            
            post_data = {
                "platform": platform,
                "content_id": self.test_data["content_id"],
                "scheduled_time": (datetime.utcnow() + timedelta(hours=2)).isoformat()
            }
            
            result = self.make_request("POST", "/social/schedule", post_data)
            if result["success"]:
                if platform == "youtube":
                    self.test_data["post_id"] = result["data"]["id"]
                self.log(f"✅ {platform} post scheduling successful")
            else:
                self.log(f"❌ {platform} post scheduling failed", "ERROR")
                success = False
                
        # Test post retrieval
        result = self.make_request("GET", "/social/posts")
        if result["success"]:
            self.log("✅ Social posts retrieval successful")
        else:
            self.log("❌ Social posts retrieval failed", "ERROR")
            success = False
            
        # Test post status update
        if "post_id" in self.test_data:
            result = self.make_request("PUT", f"/social/posts/{self.test_data['post_id']}/status", 
                                     params={"status": "posted", "post_url": "https://youtube.com/watch?v=test123"})
            if result["success"]:
                self.log("✅ Post status update successful")
            else:
                self.log("❌ Post status update failed", "ERROR")
                success = False
                
        return success

    def test_revenue_tracking(self) -> bool:
        """Test revenue tracking and statistics"""
        self.log("=== Testing Revenue Tracking ===")
        success = True
        
        if "workflow_id" not in self.test_data:
            self.log("❌ No workflow available for revenue testing", "ERROR")
            return False
            
        # Add revenue entries
        revenue_sources = [
            {"source": "affiliate", "amount": 299.99},
            {"source": "course_sale", "amount": 497.00},
            {"source": "consultation", "amount": 150.00}
        ]
        
        for revenue_data in revenue_sources:
            revenue_data.update({
                "workflow_id": self.test_data["workflow_id"],
                "currency": "EUR",
                "lead_id": self.test_data.get("lead_id")
            })
            
            result = self.make_request("POST", "/revenue", revenue_data)
            if result["success"]:
                self.log(f"✅ Revenue entry ({revenue_data['source']}) successful")
            else:
                self.log(f"❌ Revenue entry ({revenue_data['source']}) failed", "ERROR")
                success = False
                
        # Test revenue retrieval
        result = self.make_request("GET", "/revenue")
        if result["success"]:
            self.log("✅ Revenue retrieval successful")
        else:
            self.log("❌ Revenue retrieval failed", "ERROR")
            success = False
            
        return success

    def test_automation_pipeline(self) -> bool:
        """Test automated lead-to-content pipeline"""
        self.log("=== Testing Automation Pipeline ===")
        success = True
        
        if "lead_id" not in self.test_data:
            self.log("❌ No lead available for automation testing", "ERROR")
            return False
            
        # Test lead-to-content automation
        result = self.make_request("POST", f"/automation/lead-to-content/{self.test_data['lead_id']}")
        if result["success"]:
            self.log("✅ Lead-to-content automation successful")
            
            # Verify automation created content and scheduled posts
            response_data = result["data"]
            if "content" in response_data and "scheduled_posts" in response_data:
                self.log("✅ Automation created content and scheduled posts")
                self.test_data["automation_content_id"] = response_data["content"]["id"]
            else:
                self.log("⚠️ Automation response incomplete", "WARNING")
        else:
            self.log("❌ Lead-to-content automation failed", "ERROR")
            success = False
            
        # Test content recycling
        if "automation_content_id" in self.test_data:
            platforms = ["youtube", "tiktok", "linkedin"]
            result = self.make_request("POST", f"/automation/content-recycling/{self.test_data['automation_content_id']}", 
                                     {"platforms": platforms})
            if result["success"]:
                self.log("✅ Content recycling automation successful")
            else:
                self.log("❌ Content recycling automation failed", "ERROR")
                success = False
                
        return success

    def test_webhook_integration(self) -> bool:
        """Test webhook integration for external lead sources"""
        self.log("=== Testing Webhook Integration ===")
        success = True
        
        # Test webhook lead reception
        webhook_data = {
            "email": "anna.schmidt@innovativ-gmbh.de",
            "company": "Innovativ GmbH",
            "industry": "E-Commerce",
            "pain_points": ["Niedrige Conversion-Rate", "Hohe Kundenakquisitionskosten", "Ineffektive Werbung"],
            "source": "facebook_ads"
        }
        
        result = self.make_request("POST", "/webhook/lead", webhook_data)
        if result["success"]:
            self.log("✅ Webhook lead processing successful")
            
            # Verify webhook triggered automation
            response_data = result["data"]
            if "lead_id" in response_data:
                self.log("✅ Webhook created lead and triggered automation")
                self.test_data["webhook_lead_id"] = response_data["lead_id"]
            else:
                self.log("⚠️ Webhook response incomplete", "WARNING")
        else:
            self.log("❌ Webhook lead processing failed", "ERROR")
            success = False
            
        return success

    def test_analytics_stats(self) -> bool:
        """Test analytics and statistics endpoints"""
        self.log("=== Testing Analytics & Statistics ===")
        success = True
        
        result = self.make_request("GET", "/stats")
        if result["success"]:
            stats = result["data"]
            required_fields = ["total_workflows", "active_workflows", "total_leads", 
                             "total_revenue", "content_created_today", "posts_scheduled"]
            
            missing_fields = [field for field in required_fields if field not in stats]
            if not missing_fields:
                self.log("✅ Analytics stats retrieval successful")
                self.log(f"Stats: {json.dumps(stats, indent=2)}")
            else:
                self.log(f"⚠️ Analytics stats missing fields: {missing_fields}", "WARNING")
                success = False
        else:
            self.log("❌ Analytics stats retrieval failed", "ERROR")
            success = False
            
        return success

    def run_comprehensive_test(self) -> Dict[str, bool]:
        """Run all tests and return results"""
        self.log("🚀 Starting Comprehensive ZZ-LOBBY-BOOST Backend Tests")
        self.log(f"Testing against: {self.api_url}")
        
        test_results = {}
        
        # Run all test suites
        test_suites = [
            ("API Health", self.test_api_health),
            ("Workflow Management", self.test_workflow_management),
            ("Lead Management", self.test_lead_management),
            ("Content Generation (LLM)", self.test_content_generation),
            ("Social Media Management", self.test_social_media_management),
            ("Revenue Tracking", self.test_revenue_tracking),
            ("Automation Pipeline", self.test_automation_pipeline),
            ("Webhook Integration", self.test_webhook_integration),
            ("Analytics & Statistics", self.test_analytics_stats)
        ]
        
        for test_name, test_func in test_suites:
            try:
                self.log(f"\n{'='*60}")
                result = test_func()
                test_results[test_name] = result
                status = "✅ PASSED" if result else "❌ FAILED"
                self.log(f"{test_name}: {status}")
            except Exception as e:
                self.log(f"❌ {test_name} crashed: {str(e)}", "ERROR")
                test_results[test_name] = False
                
        # Summary
        self.log(f"\n{'='*60}")
        self.log("🏁 TEST SUMMARY")
        self.log(f"{'='*60}")
        
        passed = sum(1 for result in test_results.values() if result)
        total = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            self.log(f"{test_name}: {status}")
            
        self.log(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            self.log("🎉 All tests passed! ZZ-LOBBY-BOOST backend is working correctly.")
        else:
            self.log(f"⚠️ {total - passed} test(s) failed. Please check the logs above.")
            
        return test_results

def main():
    # Get backend URL from environment
    backend_url = "https://mobile-zap-setup.preview.emergentagent.com"
    
    print(f"ZZ-LOBBY-BOOST Backend Test Suite")
    print(f"Backend URL: {backend_url}")
    print(f"{'='*80}")
    
    tester = ZZLobbyBoostTester(backend_url)
    results = tester.run_comprehensive_test()
    
    # Return exit code based on results
    all_passed = all(results.values())
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())