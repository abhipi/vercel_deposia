"""
Avatar Creation Pipeline Module

This module creates expert witness avatar personas with images using OpenAI Responses API.
"""

import os
import base64
from openai import OpenAI
from typing import Dict, Any

# Try to import toml for config file parsing
try:
    import toml

    TOML_AVAILABLE = True
except ImportError:
    TOML_AVAILABLE = False

# Import prompts from the prompts package
try:
    from .prompts import (
        EXPERT_WITNESS_SYSTEM_PROMPT,
        EXPERT_WITNESS_USER_PROMPT_TEMPLATE,
    )
    from .prompts.image_generation_prompts import get_expert_image_prompt
except ImportError:
    # Fallback if prompts package is not available
    EXPERT_WITNESS_SYSTEM_PROMPT = "You are an expert witness persona creator."
    EXPERT_WITNESS_USER_PROMPT_TEMPLATE = (
        "Create an expert witness persona based on: {user_query}"
    )

    def get_expert_image_prompt(expert_type="general", user_description=""):
        return "Create a professional headshot portrait of an expert witness."


# Default configuration
DEFAULT_CONFIG = {
    "openai": {
        "chat_model": "gpt-4o",
        "image_model": "gpt-4o",  # Using GPT-4o for image generation via Responses API
        "max_tokens": 1500,
        "temperature": 0.7,
    },
    "image_generation": {
        "size": "1024x1536",  # Portrait format
        "quality": "medium",  # Medium quality as requested
        "background": "transparent",
        "output_format": "png",
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


def create_avatar_image(
    text_query: str, expert_type: str = "general"
) -> Dict[str, Any]:
    """
    Create an expert witness persona and generate an avatar image using OpenAI Responses API.

    Args:
        text_query (str): User's text query describing the expert witness needed
        expert_type (str): Type of expert (technical, medical, financial, academic, general)

    Returns:
        dict: Result containing persona details and image data
    """
    try:
        # Get OpenAI API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return {
                "status": "error",
                "message": "OpenAI API key not found in environment variables",
            }

        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)

        # Get configuration values
        chat_model = CONFIG["openai"]["chat_model"]
        max_tokens = CONFIG["openai"]["max_tokens"]
        temperature = CONFIG["openai"]["temperature"]
        image_size = CONFIG["image_generation"]["size"]
        image_quality = CONFIG["image_generation"]["quality"]
        image_background = CONFIG["image_generation"]["background"]

        # Step 1: Generate expert witness persona using GPT-4o
        persona_prompt = EXPERT_WITNESS_USER_PROMPT_TEMPLATE.format(
            user_query=text_query
        )

        persona_response = client.chat.completions.create(
            model=chat_model,
            messages=[
                {"role": "system", "content": EXPERT_WITNESS_SYSTEM_PROMPT},
                {"role": "user", "content": persona_prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )

        expert_persona = persona_response.choices[0].message.content

        # Step 2: Generate avatar image using Responses API with image_generation tool
        image_prompt = get_expert_image_prompt(expert_type, text_query)

        # Use Responses API with image generation tool
        response = client.responses.create(
            model=chat_model,
            input=f"Create a professional expert witness avatar image: {image_prompt}",
            tools=[
                {
                    "type": "image_generation",
                    "size": image_size,
                    "quality": image_quality,
                    "background": image_background,
                }
            ],
        )

        # Extract image data from response
        image_data = [
            output.result
            for output in response.output
            if output.type == "image_generation_call"
        ]

        if not image_data:
            return {
                "status": "error",
                "message": "No image was generated in the response",
            }

        # Convert base64 image to data URL
        image_base64 = image_data[0]
        image_url = f"data:image/png;base64,{image_base64}"

        return {
            "status": "ok",
            "message": "Expert witness avatar created successfully",
            "data": {
                "persona": expert_persona,
                "image_url": image_url,
                "expert_type": expert_type,
                "query": text_query,
                "avatar_id": f"expert_{hash(text_query) % 10000}",
                "models_used": {"chat": chat_model, "image": chat_model},
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
        "image_model": CONFIG["openai"]["image_model"],
    }
