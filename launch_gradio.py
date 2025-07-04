#!/usr/bin/env python3
"""
Launch script for the Expert Witness Avatar Creator Gradio app.

This script provides an easy way to start the Gradio interface for creating
expert witness personas from PDF documents.
"""

import os
import sys
import subprocess
from gradio_app import main


def check_pipenv():
    """Check if pipenv is installed and available."""
    try:
        subprocess.run(["pipenv", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_environment():
    """Check if required environment variables are set."""
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables before running the app.")
        print("Example: export OPENAI_API_KEY='your-api-key-here'")
        return False

    return True


def print_instructions():
    """Print usage instructions."""
    print(
        """
🎯 Expert Witness Avatar Creator
================================

This Gradio app allows you to:
1. Upload PDF documents
2. Extract text content
3. Generate expert witness personas using OpenAI GPT-4o
4. Create professional avatar images using DALL-E

Prerequisites:
- Deposia API server running on http://localhost:8000
- OpenAI API key set as environment variable
- Pipenv environment set up

Setup Instructions:
1. Install pipenv: pip install pipenv
2. Install dependencies: pipenv install
3. Set environment variables in .env file or export them
4. Start API server: pipenv run uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload

Starting Gradio app...
"""
    )


if __name__ == "__main__":
    print_instructions()

    # Check if pipenv is available
    if not check_pipenv():
        print("❌ pipenv not found. Please install it with: pip install pipenv")
        sys.exit(1)

    # Check environment variables
    if not check_environment():
        sys.exit(1)

    # Launch the Gradio app
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Gradio app stopped.")
    except Exception as e:
        print(f"❌ Error starting Gradio app: {e}")
        sys.exit(1)
