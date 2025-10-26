#!/usr/bin/env python3
"""
Comprehensive API Endpoint Test Script
Tests ALL available endpoints to ensure they're working correctly.
"""

import requests
import json
import time
import sys

# Flask API configuration
FLASK_BASE_URL = "http://localhost:5003"

class EndpointTester:
    def __init__(self):
        self.project_id = None
        self.test_results = {}
        
    def print_header(self, title: str):
        """Print a formatted header."""
        print(f"\n{'='*80}")
        print(f"🔥 {title}")
        print(f"{'='*80}")
    
    def print_result(self, endpoint: str, success: bool, message: str = "", error: str = ""):
        """Print test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {endpoint}")
        if message:
            print(f"   📝 {message}")
        if error:
            print(f"   ❌ {error}")
        
        self.test_results[endpoint] = {
            "success": success,
            "message": message,
            "error": error
        }
    
    def test_endpoint(self, method: str, endpoint: str, data: dict = None, timeout: int = 10):
        """Test a single endpoint."""
        try:
            url = f"{FLASK_BASE_URL}{endpoint}"
            
            if method.upper() == "GET":
                response = requests.get(url, timeout=timeout)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code == 200:
                result = response.json()
                self.print_result(endpoint, True, f"Status: {response.status_code}")
                return result
            else:
                self.print_result(endpoint, False, f"Status: {response.status_code}", f"Response: {response.text}")
                return None
                
        except Exception as e:
            self.print_result(endpoint, False, "", str(e))
            return None
    
    def run_all_tests(self):
        """Run tests for all endpoints."""
        self.print_header("COMPREHENSIVE API ENDPOINT TEST")
        
        # Test 1: Health Check
        self.print_header("TEST 1: Health Check")
        health_result = self.test_endpoint("GET", "/api/health")
        if not health_result:
            print("❌ Server not running! Please start the Flask server first.")
            return False
        
        # Test 2: Get Agents Info
        self.print_header("TEST 2: Get Agents Info")
        agents_result = self.test_endpoint("GET", "/api/agents")
        
        # Test 3: Submit Project
        self.print_header("TEST 3: Submit Project")
        project_data = {"project_description": "Build a comprehensive todo application with user authentication"}
        project_result = self.test_endpoint("POST", "/api/submit-project", project_data)
        
        if project_result and project_result.get('success'):
            self.project_id = project_result.get('project_id')
            print(f"📋 Project ID: {self.project_id}")
            print(f"📋 Subtasks: {len(project_result.get('subtasks', []))}")
        
        # Test 4: Create Agents
        self.print_header("TEST 4: Create Agents")
        if self.project_id:
            agents_data = {"project_id": self.project_id}
            create_result = self.test_endpoint("POST", "/api/create-agents", agents_data, timeout=60)
        
        # Test 5: Start Work
        self.print_header("TEST 5: Start Work")
        if self.project_id:
            work_data = {"project_id": self.project_id, "subtask_id": 1}
            work_result = self.test_endpoint("POST", "/api/start-work", work_data)
        
        # Test 6: Get Results (Send subtask to agents)
        self.print_header("TEST 6: Get Results")
        if self.project_id:
            results_data = {
                "project_id": self.project_id,
                "agent_names": ["One"]  # Test with one agent for speed
            }
            results_result = self.test_endpoint("POST", "/api/get-results", results_data, timeout=60)
        
        # Test 7: Retrieve Code
        self.print_header("TEST 7: Retrieve Code")
        if self.project_id:
            retrieve_data = {
                "project_id": self.project_id,
                "agent_name": "One"
            }
            code_result = self.test_endpoint("POST", "/api/retrieve-code", retrieve_data, timeout=30)
            
            if code_result and code_result.get('success'):
                code = code_result.get('code', '')
                print(f"📏 Code Length: {len(code)} characters")
                if code:
                    print("📄 Code Preview:")
                    print("-" * 40)
                    print(code[:200] + "..." if len(code) > 200 else code)
                    print("-" * 40)
        
        # Test 8: Progress Messages
        self.print_header("TEST 8: Progress Messages")
        if self.project_id:
            progress_result = self.test_endpoint("GET", f"/api/progress-messages?project_id={self.project_id}")
        
        # Test 9: Agent Stats
        self.print_header("TEST 9: Agent Stats")
        if self.project_id:
            stats_result = self.test_endpoint("GET", f"/api/agent-stats?project_id={self.project_id}")
        
        # Test 10: Project Status
        self.print_header("TEST 10: Project Status")
        if self.project_id:
            status_result = self.test_endpoint("GET", f"/api/project-status?project_id={self.project_id}")
        
        # Test 11: Select Winner
        self.print_header("TEST 11: Select Winner")
        if self.project_id:
            winner_data = {
                "project_id": self.project_id,
                "winner": "One",
                "reason": "Clean, efficient code with personality"
            }
            winner_result = self.test_endpoint("POST", "/api/select-winner", winner_data)
        
        # Test 12: Complete Round
        self.print_header("TEST 12: Complete Round")
        if self.project_id:
            complete_data = {
                "project_id": self.project_id,
                "subtask_id": 1,
                "winner": "One",
                "winner_code": "// Sample winner code for testing"
            }
            complete_result = self.test_endpoint("POST", "/api/complete-round", complete_data)
        
        # Test 13: Get Messages (Debug endpoint)
        self.print_header("TEST 13: Get Messages (Debug)")
        if self.project_id:
            messages_data = {
                "project_id": self.project_id,
                "agent_name": "One"
            }
            messages_result = self.test_endpoint("POST", "/api/get-messages", messages_data, timeout=30)
            
            if messages_result and messages_result.get('success'):
                message_count = messages_result.get('message_count', 0)
                print(f"📊 Found {message_count} messages from Agent One")
        
        # Test 14: Get Commentary
        self.print_header("TEST 14: Get Commentary")
        if self.project_id:
            commentary_data = {
                "project_id": self.project_id,
                "subtask_id": "1"
            }
            commentary_result = self.test_endpoint("POST", "/api/get-commentary", commentary_data, timeout=30)
            
            if commentary_result and commentary_result.get('success'):
                commentary = commentary_result.get('commentary', '')
                print(f"📝 Commentary Length: {len(commentary)} characters")
                if commentary:
                    print("🎙️ Commentary Preview:")
                    print("-" * 40)
                    print(commentary[:150] + "..." if len(commentary) > 150 else commentary)
                    print("-" * 40)
        
        # Test 15: Get Chat Summary
        self.print_header("TEST 15: Get Chat Summary")
        if self.project_id:
            summary_data = {
                "project_id": self.project_id,
                "subtask_id": "1"
            }
            summary_result = self.test_endpoint("POST", "/api/get-chat-summary", summary_data, timeout=30)
            
            if summary_result and summary_result.get('success'):
                summary = summary_result.get('summary', '')
                print(f"📝 Summary Length: {len(summary)} characters")
                if summary:
                    print("📄 Summary Preview:")
                    print("-" * 40)
                    print(summary[:150] + "..." if len(summary) > 150 else summary)
                    print("-" * 40)
        
        # Test 16: Orchestrate Project
        self.print_header("TEST 16: Orchestrate Project")
        orchestrate_data = {
            "project_description": "Build a simple calculator app"
        }
        orchestrate_result = self.test_endpoint("POST", "/api/orchestrate-project", orchestrate_data, timeout=30)
        
        if orchestrate_result and orchestrate_result.get('success'):
            subtasks = orchestrate_result.get('subtasks', [])
            print(f"📋 Generated {len(subtasks)} subtasks:")
            for i, subtask in enumerate(subtasks, 1):
                print(f"  {i}. {subtask.get('title', 'Unknown')}: {subtask.get('description', 'No description')[:50]}...")
        
        # Summary
        self.print_header("TEST SUMMARY")
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Endpoints:")
            for endpoint, result in self.test_results.items():
                if not result['success']:
                    print(f"   • {endpoint}: {result['error']}")
        
        print(f"\n🎯 All endpoints tested!")
        return failed_tests == 0

def main():
    """Main test function."""
    print("🧪 Comprehensive API Endpoint Test")
    print("Testing ALL available endpoints...")
    
    tester = EndpointTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! API is fully functional.")
        sys.exit(0)
    else:
        print("\n⚠️ Some tests failed. Check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
