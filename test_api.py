"""
Test script for Deposia Expert Witness Avatar Creator API

Tests the simplified API endpoints using Together AI for image generation.
"""

import requests
import json
import time

# API Configuration
API_BASE_URL = "https://vercel-deposia.vercel.app"


def test_health_endpoint():
    """Test the basic health check endpoint."""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False


def test_avatar_status_endpoint():
    """Test the avatar status endpoint."""
    print("\n🔍 Testing avatar status endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/avatar/status", timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Avatar status check passed: {data}")
            return True
        else:
            print(f"❌ Avatar status check failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Avatar status error: {e}")
        return False


def test_create_avatar_endpoint():
    """Test the avatar creation endpoint with simplified query."""
    print("\n🔍 Testing avatar creation endpoint...")

    # Simple test case
    test_payload = {
        "text_query": "Medical malpractice case involving surgical complications and patient safety protocols"
    }

    try:
        print(f"Sending request with payload: {json.dumps(test_payload, indent=2)}")

        response = requests.post(
            f"{API_BASE_URL}/api/create_avatar",
            json=test_payload,
            timeout=120,  # Extended timeout for AI generation
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Avatar creation successful!")
            print(f"Status: {data.get('status')}")
            print(f"Message: {data.get('message')}")

            if "data" in data:
                avatar_data = data["data"]
                print("\nGenerated Avatar Data:")
                print(f"- Avatar ID: {avatar_data.get('avatar_id')}")
                print(f"- Expert Type: {avatar_data.get('expert_type')}")
                print(f"- Models Used: {avatar_data.get('models_used')}")
                print(f"- Image URL: {avatar_data.get('image_url')}")
                print(f"- Persona Length: {len(avatar_data.get('persona', ''))}")

                # Display first 200 characters of persona
                persona = avatar_data.get("persona", "")
                if persona:
                    print(f"- Persona Preview: {persona[:200]}...")

            return True
        else:
            print(f"❌ Avatar creation failed: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("❌ Request timed out - avatar generation takes time")
        return False
    except Exception as e:
        print(f"❌ Avatar creation error: {e}")
        return False


def run_comprehensive_test():
    """Run all tests and provide a summary."""
    print("🚀 Starting Deposia API Comprehensive Test")
    print("=" * 60)

    test_results = {}

    # Run all tests
    test_results["health"] = test_health_endpoint()
    test_results["avatar_status"] = test_avatar_status_endpoint()
    test_results["create_avatar"] = test_create_avatar_endpoint()

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    total_tests = len(test_results)
    passed_tests = sum(test_results.values())

    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<15}: {status}")

    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("🎉 All tests passed! The API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the API configuration.")

    return passed_tests == total_tests


if __name__ == "__main__":
    success = run_comprehensive_test()
    exit(0 if success else 1)
