"""
Avatar Creation Pipeline Module

This module creates expert witness personas with images using OpenAI GPT and Together AI.
"""

import os
import requests
from openai import OpenAI
from typing import Dict, Any

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


def create_avatar_image(text_query: str) -> Dict[str, Any]:
    """
    Create an expert witness persona and generate an avatar image.

    Args:
        text_query (str): User's text query describing the case

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

        # Initialize OpenAI client for text generation
        openai_client = OpenAI(api_key=openai_api_key)

        # Get configuration values
        chat_model = CONFIG["openai"]["chat_model"]
        max_tokens = CONFIG["openai"]["max_tokens"]
        temperature = CONFIG["openai"]["temperature"]
        image_model = CONFIG["together_ai"]["image_model"]

        # Step 1: Generate expert witness persona using GPT-4o
        persona_prompt = EXPERT_WITNESS_USER_PROMPT_TEMPLATE.format(
            user_query=text_query
        )

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
        image_prompt = get_simple_image_prompt(text_query)

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
            "message": "Expert witness avatar created successfully",
            "data": {
                "persona": expert_persona,
                "image_url": image_url,
                "query": text_query,
                "avatar_id": f"expert_{hash(text_query) % 10000}",
                "models_used": {"chat": chat_model, "image": image_model},
            },
        }

    except Exception as e:
        return {"status": "error", "message": f"Error creating avatar: {str(e)}"}


def get_avatar_status():
    """Get the status of the avatar creation pipeline."""
    return {
        "status": "ok",
        "message": "Avatar creation pipeline is operational",
        "chat_model": CONFIG["openai"]["chat_model"],
        "image_model": CONFIG["together_ai"]["image_model"],
    }
