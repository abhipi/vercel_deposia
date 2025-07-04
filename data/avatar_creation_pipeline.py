"""
Avatar Creation Pipeline Module

This module creates expert witness personas with images using OpenAI GPT and Together AI.
Supports both text queries and PDF file uploads.
"""

import os
import requests
import asyncio
import io
from openai import OpenAI
from typing import Dict, Any, List, Optional
from fastapi import UploadFile
import PyPDF2

# Try to import toml for config file parsing
try:
    import toml

    TOML_AVAILABLE = True
except ImportError:
    TOML_AVAILABLE = False

# Simple prompts - keep it minimal
EXPERT_WITNESS_SYSTEM_PROMPT = "You are an expert witness creator. Create professional expert witness personas based on legal case content."

EXPERT_WITNESS_USER_PROMPT_TEMPLATE = (
    "Create a professional expert witness persona for this case: {user_query}"
)


def get_simple_image_prompt(user_description=""):
    """Generate a simple, direct image prompt."""
    return (
        f"Professional headshot portrait of an expert witness for: {user_description}"
    )


# Default configuration
DEFAULT_CONFIG = {
    "openai": {
        "chat_model": "gpt-4o",
        "max_tokens": 1000,
        "temperature": 0.7,
    },
    "together_ai": {
        "image_model": "black-forest-labs/FLUX.1-schnell",
        "max_tokens": 512,
        "temperature": 0.7,
    },
}


def load_config():
    """Load configuration from config.toml file."""
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.toml")

    if not TOML_AVAILABLE:
        return DEFAULT_CONFIG

    try:
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                return toml.load(f)
        else:
            return DEFAULT_CONFIG
    except Exception:
        return DEFAULT_CONFIG


# Load configuration
CONFIG = load_config()


async def extract_text_from_pdf(file: UploadFile) -> str:
    """Extract text from a PDF file."""
    try:
        # Read the file content
        content = await file.read()

        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))

        # Extract text from all pages
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"

        return text.strip()
    except Exception as e:
        raise Exception(f"Error extracting text from {file.filename}: {str(e)}")


async def process_multiple_pdfs(files: List[UploadFile]) -> str:
    """Process multiple PDF files and combine their text content."""
    all_text = []

    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            raise Exception(f"File {file.filename} is not a PDF")

        text = await extract_text_from_pdf(file)
        all_text.append(f"--- Content from {file.filename} ---\n{text}")

    return "\n\n".join(all_text)


async def create_avatar_image(
    text_query: Optional[str] = None, files: Optional[List[UploadFile]] = None
) -> Dict[str, Any]:
    """
    Create an expert witness persona and generate an avatar image.

    Args:
        text_query (str, optional): User's text query describing the case
        files (List[UploadFile], optional): PDF files to process

    Returns:
        dict: Result containing persona details and image URL
    """
    try:
        # Get API keys from environment
        openai_api_key = os.getenv("OPENAI_API_KEY")
        together_api_key = os.getenv("TOGETHER_API_KEY")

        if not openai_api_key:
            return {
                "status": "error",
                "message": "OpenAI API key not found in environment variables",
            }

        if not together_api_key:
            return {
                "status": "error",
                "message": "Together AI API key not found in environment variables",
            }

        # Process input content
        content = ""
        source_info = ""

        if files:
            # Extract text from PDF files
            pdf_content = await process_multiple_pdfs(files)
            content = pdf_content
            source_info = f"from {len(files)} PDF file(s)"

            # If text_query is also provided, combine them
            if text_query:
                content = f"Additional context: {text_query}\n\n{pdf_content}"
                source_info = f"from text query and {len(files)} PDF file(s)"
        else:
            content = text_query
            source_info = "from text query"

        # Initialize OpenAI client for text generation
        openai_client = OpenAI(api_key=openai_api_key)

        # Get configuration values
        chat_model = CONFIG["openai"]["chat_model"]
        max_tokens = CONFIG["openai"]["max_tokens"]
        temperature = CONFIG["openai"]["temperature"]
        image_model = CONFIG["together_ai"]["image_model"]

        # Step 1: Generate expert witness persona using GPT-4o
        persona_prompt = EXPERT_WITNESS_USER_PROMPT_TEMPLATE.format(user_query=content)

        persona_response = openai_client.chat.completions.create(
            model=chat_model,
            messages=[
                {"role": "system", "content": EXPERT_WITNESS_SYSTEM_PROMPT},
                {"role": "user", "content": persona_prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )

        expert_persona = persona_response.choices[0].message.content

        # Step 2: Generate avatar image using Together AI FLUX
        # Use a simplified description for image generation
        image_description = text_query if text_query else "legal case content"
        image_prompt = get_simple_image_prompt(image_description)

        together_response = requests.post(
            "https://api.together.xyz/v1/images/generations",
            headers={
                "Authorization": f"Bearer {together_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": image_model,
                "prompt": image_prompt,
                "width": 1024,
                "height": 768,
                "steps": 3,
                "n": 1,
                "response_format": "url",
            },
            timeout=60,
        )

        if together_response.status_code != 200:
            return {
                "status": "error",
                "message": f"Together AI API error: {together_response.status_code} - {together_response.text}",
            }

        image_data = together_response.json()
        image_url = image_data["data"][0]["url"]

        return {
            "status": "ok",
            "message": f"Expert witness avatar created successfully {source_info}",
            "data": {
                "persona": expert_persona,
                "image_url": image_url,
                "query": text_query or "PDF content",
                "files_processed": [f.filename for f in files] if files else [],
                "avatar_id": f"expert_{hash(content) % 10000}",
                "models_used": {"chat": chat_model, "image": image_model},
            },
        }

    except Exception as e:
        return {"status": "error", "message": f"Error creating avatar: {str(e)}"}


# Keep the synchronous version for backward compatibility
def create_avatar_image_sync(text_query: str) -> Dict[str, Any]:
    """Synchronous version for backward compatibility."""
    return asyncio.run(create_avatar_image(text_query=text_query))


def get_avatar_status():
    """Get the status of the avatar creation pipeline."""
    return {
        "status": "ok",
        "message": "Avatar creation pipeline is operational",
        "chat_model": CONFIG["openai"]["chat_model"],
        "image_model": CONFIG["together_ai"]["image_model"],
    }
