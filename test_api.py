#!/usr/bin/env python3
"""
Test script to verify the hosted Deposia API is working correctly.
"""

import requests
import json
from datetime import datetime

# API Configuration
API_BASE_URL = "https://vercel-deposia-git-main-abhipis-projects.vercel.app"
ENDPOINTS = {
    "health": f"{API_BASE_URL}/",
    "detailed_health": f"{API_BASE_URL}/health",
    "avatar_status": f"{API_BASE_URL}/avatar/status",
    "avatar_create": f"{API_BASE_URL}/avatar/create-image"
}

def test_endpoint(name, url, method="GET", data=None):
    """Test a single API endpoint."""
    print(f"\n🔍 Testing {name}...")
    print(f"   URL: {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                print(f"   Response: {json.dumps(json_data, indent=2)}")
                return True
            except json.JSONDecodeError:
                print(f"   Response: {response.text}")
                return True
        else:
            print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   Connection Error: {str(e)}")
        return False

def main():
    """Run all API tests."""
    print("🎯 Deposia API Test Suite")
    print("=" * 50)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 API Base URL: {API_BASE_URL}")
    
    results = {}
    
    # Test basic health check
    results["health"] = test_endpoint("Health Check", ENDPOINTS["health"])
    
    # Test detailed health check
    results["detailed_health"] = test_endpoint("Detailed Health", ENDPOINTS["detailed_health"])
    
    # Test avatar status
    results["avatar_status"] = test_endpoint("Avatar Status", ENDPOINTS["avatar_status"])
    
    # Test avatar creation (light test)
    avatar_test_data = {
        "text_query": "Test query for API verification",
        "expert_type": "general"
    }
    results["avatar_create"] = test_endpoint(
        "Avatar Creation", 
        ENDPOINTS["avatar_create"], 
        method="POST", 
        data=avatar_test_data
    )
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for endpoint, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {endpoint}: {status}")
    
    print(f"\n🏆 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the API deployment.")

if __name__ == "__main__":
    main() 