"""
Test script for the Deposia Expert Witness Avatar Creator API.
Tests the clean API structure with persona and avatar endpoints.
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


def test_pipeline_status():
    """Test the pipeline status endpoint."""
    print("\nTesting pipeline status endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/status")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_create_avatar_text():
    """Test creating an avatar (persona + image) with text query."""
    print("\nTesting create avatar with text query...")
    try:
        data = {
            "text_query": "Construction defect case requiring structural engineering expert witness"
        }
        response = requests.post(f"{BASE_URL}/api/avatar", data=data)
        print(f"Status Code: {response.status_code}")
        response_data = response.json()
        print(f"Response: {json.dumps(response_data, indent=2)}")

        # Check if response contains both persona and image
        if response.status_code == 200 and response_data.get("status") == "ok":
            data = response_data.get("data", {})
            has_persona = "persona" in data
            has_image = "image_url" in data
            has_summary = "persona_summary" in data
            print(f"✓ Has persona: {has_persona}")
            print(f"✓ Has image: {has_image}")
            print(f"✓ Has persona summary: {has_summary}")
            return has_persona and has_image and has_summary

        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_create_persona_text():
    """Test creating just a persona (no image) with text query."""
    print("\nTesting create persona only with text query...")
    try:
        data = {
            "text_query": "Medical malpractice case requiring expert witness in cardiology"
        }
        response = requests.post(f"{BASE_URL}/api/persona", data=data)
        print(f"Status Code: {response.status_code}")
        response_data = response.json()
        print(f"Response: {json.dumps(response_data, indent=2)}")

        # Check if response contains persona but no image
        if response.status_code == 200 and response_data.get("status") == "ok":
            data = response_data.get("data", {})
            has_persona = "persona" in data
            has_no_image = "image_url" not in data
            has_no_summary = "persona_summary" not in data
            print(f"✓ Has persona: {has_persona}")
            print(f"✓ No image URL: {has_no_image}")
            print(f"✓ No persona summary: {has_no_summary}")
            return has_persona and has_no_image and has_no_summary

        return False
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

        response = requests.post(f"{BASE_URL}/api/avatar", files=files, data=data)
        print(f"Status Code: {response.status_code}")
        response_data = response.json()
        print(f"Response: {json.dumps(response_data, indent=2)}")

        # Check if response contains both persona and image
        if response.status_code == 200 and response_data.get("status") == "ok":
            data = response_data.get("data", {})
            has_persona = "persona" in data
            has_image = "image_url" in data
            has_files = "files_processed" in data
            print(f"✓ Has persona: {has_persona}")
            print(f"✓ Has image: {has_image}")
            print(f"✓ Has files processed: {has_files}")
            return has_persona and has_image and has_files

        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_create_persona_pdf():
    """Test creating just a persona with PDF file upload."""
    print("\nTesting create persona only with PDF upload...")
    try:
        # Create test PDF content
        pdf_content = create_test_pdf()

        # Prepare files for upload
        files = [
            ("files", ("test_case.pdf", pdf_content, "application/pdf")),
        ]

        response = requests.post(f"{BASE_URL}/api/persona", files=files)
        print(f"Status Code: {response.status_code}")
        response_data = response.json()
        print(f"Response: {json.dumps(response_data, indent=2)}")

        # Check if response contains persona but no image
        if response.status_code == 200 and response_data.get("status") == "ok":
            data = response_data.get("data", {})
            has_persona = "persona" in data
            has_no_image = "image_url" not in data
            has_files = "files_processed" in data
            print(f"✓ Has persona: {has_persona}")
            print(f"✓ No image URL: {has_no_image}")
            print(f"✓ Has files processed: {has_files}")
            return has_persona and has_no_image and has_files

        return False
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

        response = requests.post(f"{BASE_URL}/api/avatar", files=files)
        print(f"Status Code: {response.status_code}")
        response_data = response.json()
        print(f"Response: {json.dumps(response_data, indent=2)}")

        # Check if response contains both persona and image
        if response.status_code == 200 and response_data.get("status") == "ok":
            data = response_data.get("data", {})
            has_persona = "persona" in data
            has_image = "image_url" in data
            files_processed = data.get("files_processed", [])
            print(f"✓ Has persona: {has_persona}")
            print(f"✓ Has image: {has_image}")
            print(f"✓ Files processed: {len(files_processed)}")
            return has_persona and has_image and len(files_processed) == 2

        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Run all tests."""
    print("Testing Deposia Expert Witness Avatar Creator API")
    print("=" * 50)

    tests = [
        test_health_check,
        test_pipeline_status,
        test_create_avatar_text,
        test_create_persona_text,
        test_create_avatar_pdf,
        test_create_persona_pdf,
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
        "Pipeline Status",
        "Create Avatar (Text)",
        "Create Persona Only (Text)",
        "Create Avatar (PDF)",
        "Create Persona Only (PDF)",
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
