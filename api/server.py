"""
Simplified FastAPI server for Deposia Expert Witness Avatar Creation.
Only 3 endpoints: health, avatar status, and create avatar.
"""

from __future__ import annotations
import json
import os
import sys
import asyncio
import importlib.util
from pydantic import BaseModel, Field
from typing import List, AsyncGenerator, Awaitable

from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging

# Suppress excessive logging
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.CRITICAL)

load_dotenv(override=True)

####################################################################################################
# SETUP FOR DYNAMIC IMPORTS FROM DATA FOLDER
####################################################################################################
TEMP_DIR = "/tmp"
DATA_FOLDER = "data"

os.makedirs(TEMP_DIR, exist_ok=True)


####################################################################################################
# UTILITY FUNCTIONS FOR DYNAMIC IMPORTS
####################################################################################################
def dynamic_import(module_path, module_name, required_attrs=None):
    """
    Dynamically import a module from the specified path.

    Args:
        module_path: Path to the module file
        module_name: Name to assign to the module
        required_attrs: List of required attributes/functions to verify

    Returns:
        The imported module
    """
    if not os.path.exists(module_path):
        raise FileNotFoundError(f"Could not find {module_path}")

    # Add the module's directory to sys.path if not already present
    module_dir = os.path.dirname(module_path)
    if module_dir not in sys.path:
        sys.path.insert(0, os.path.abspath(module_dir))

    try:
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load spec for {module_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Verify required attributes exist
        if required_attrs:
            for attr in required_attrs:
                if not hasattr(module, attr):
                    raise AttributeError(
                        f"'{attr}' not found in module '{module_name}'"
                    )

        return module

    except Exception as e:
        raise ImportError(f"Failed to import '{module_path}': {str(e)}")


####################################################################################################
# IMPORT AVATAR CREATION PIPELINE
####################################################################################################
# Import the avatar creation pipeline module
try:
    avatar_pipeline = dynamic_import(
        module_path=os.path.join(DATA_FOLDER, "avatar_creation_pipeline.py"),
        module_name="avatar_pipeline",
        required_attrs=["create_avatar_image"],
    )
    create_avatar_image = avatar_pipeline.create_avatar_image
    get_avatar_status = avatar_pipeline.get_avatar_status
except (FileNotFoundError, ImportError, AttributeError) as e:
    logger.warning(f"Could not import avatar pipeline: {e}")
    create_avatar_image = None
    get_avatar_status = None

####################################################################################################
# FASTAPI APP
####################################################################################################
app = FastAPI(title="Deposia Expert Witness Avatar Creator", version="1.0.0")

# Define allowed origins
origins = [
    "*",  # Allow all origins (update this for production)
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


####################################################################################################
# API ENDPOINTS - ONLY 3 TOTAL
####################################################################################################


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Server is healthy",
        "data_folder_exists": os.path.exists(DATA_FOLDER),
        "temp_dir_exists": os.path.exists(TEMP_DIR),
    }


@app.get("/avatar/status")
async def avatar_status():
    """Get the status of the avatar creation pipeline."""
    if get_avatar_status is None:
        raise HTTPException(status_code=500, detail="Avatar pipeline not available")

    return get_avatar_status()


class AvatarRequest(BaseModel):
    text_query: str = Field(..., description="Case description or legal content")


@app.post("/api/create_avatar")
async def create_avatar(request: AvatarRequest):
    """Create an expert witness persona and avatar from case content."""
    if create_avatar_image is None:
        raise HTTPException(
            status_code=500, detail="Avatar creation pipeline not available"
        )

    return create_avatar_image(request.text_query)
