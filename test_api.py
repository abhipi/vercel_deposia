"""
Test script for the Deposia Expert Witness Avatar Creator API.
Tests all 3 endpoints including PDF upload functionality.
"""

import requests
import json
import os
import io
import time

# Configuration
BASE_URL = "http://localhost:8000"  # Change this for your deployment
TEST_PDF_CONTENT = """Sample Legal Case Document

Case Overview:
This is a sample legal case involving construction defects in a commercial building. 
The case requires expert testimony from a structural engineer with experience in 
commercial construction and building code compliance.

Key Issues:
- Foundation settlement causing structural damage
- Improper waterproofing leading to water intrusion
- Non-compliance with local building codes
- Estimated damages exceed $2 million

Expert Requirements:
- Licensed structural engineer
- 15+ years commercial construction experience
- Expert witness experience in similar cases
- Knowledge of applicable building codes
"""


def create_test_pdf():
    """Create a simple test PDF file in memory."""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)

        # Add text to the PDF
        text_lines = TEST_PDF_CONTENT.split("\n")
        y_position = 750

        for line in text_lines:
            if line.strip():
                p.drawString(50, y_position, line)
                y_position -= 20
                if y_position < 50:  # Start new page if needed
                    p.showPage()
                    y_position = 750

        p.save()
        buffer.seek(0)
        return buffer.getvalue()
    except ImportError:
        # If reportlab is not available, create a simple text file
        print("Note: reportlab not available, creating simple text file for testing")
        return TEST_PDF_CONTENT.encode("utf-8")


def test_health_check():
    """Test the health check endpoint."""
    print("Testing health check endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_avatar_status():
    """Test the avatar status endpoint."""
    print("\nTesting avatar status endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/avatar/status")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_create_avatar_text():
    """Test creating an avatar with text query."""
    print("\nTesting create avatar with text query...")
    try:
        data = {
            "text_query": "Construction defect case requiring structural engineering expert witness"
        }
        response = requests.post(f"{BASE_URL}/api/create_avatar", data=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_create_avatar_pdf():
    """Test creating an avatar with PDF file upload."""
    print("\nTesting create avatar with PDF upload...")
    try:
        # Create test PDF content
        pdf_content = create_test_pdf()

        # Prepare files for upload
        files = [
            ("files", ("test_case.pdf", pdf_content, "application/pdf")),
        ]

        data = {
            "text_query": "Additional context: This case requires immediate expert consultation"
        }

        response = requests.post(
            f"{BASE_URL}/api/create_avatar", files=files, data=data
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_create_avatar_multiple_pdfs():
    """Test creating an avatar with multiple PDF files."""
    print("\nTesting create avatar with multiple PDF uploads...")
    try:
        # Create test PDF content
        pdf_content1 = create_test_pdf()
        pdf_content2 = TEST_PDF_CONTENT.replace(
            "Case Overview:", "Additional Case Details:"
        ).encode("utf-8")

        # Prepare multiple files for upload
        files = [
            ("files", ("case_summary.pdf", pdf_content1, "application/pdf")),
            ("files", ("case_details.pdf", pdf_content2, "application/pdf")),
        ]

        response = requests.post(f"{BASE_URL}/api/create_avatar", files=files)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Run all tests."""
    print("Testing Deposia Expert Witness Avatar Creator API")
    print("=" * 50)

    tests = [
        test_health_check,
        test_avatar_status,
        test_create_avatar_text,
        test_create_avatar_pdf,
        test_create_avatar_multiple_pdfs,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
            time.sleep(1)  # Brief pause between tests
        except Exception as e:
            print(f"Test failed with exception: {e}")
            results.append(False)

    print("\n" + "=" * 50)
    print("Test Results Summary:")
    test_names = [
        "Health Check",
        "Avatar Status",
        "Create Avatar (Text)",
        "Create Avatar (PDF)",
        "Create Avatar (Multiple PDFs)",
    ]

    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {name}: {status}")

    passed = sum(results)
    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed")


if __name__ == "__main__":
    main()
