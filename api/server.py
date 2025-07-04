"""
Simplified FastAPI server for Deposia Expert Witness Avatar Creation.
Clean API structure with persona and avatar endpoints.
"""

from __future__ import annotations
import json
import os
import sys
import asyncio
import importlib.util
from pydantic import BaseModel, Field
from typing import List, AsyncGenerator, Awaitable, Optional

from fastapi import FastAPI, Query, HTTPException, Request, File, UploadFile, Form
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
    create_persona_only = avatar_pipeline.create_persona_only
    get_avatar_status = avatar_pipeline.get_avatar_status
except (FileNotFoundError, ImportError, AttributeError) as e:
    logger.warning(f"Could not import avatar pipeline: {e}")
    create_avatar_image = None
    create_persona_only = None
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
# API ENDPOINTS - CLEAN STRUCTURE
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


@app.get("/api/status")
async def pipeline_status():
    """Get the status of the avatar creation pipeline."""
    if get_avatar_status is None:
        raise HTTPException(status_code=500, detail="Avatar pipeline not available")

    return get_avatar_status()


class AvatarRequest(BaseModel):
    text_query: str = Field(..., description="Case description or legal content")


@app.post("/api/avatar")
async def create_avatar_endpoint(
    text_query: Optional[str] = Form(
        None, description="Case description or legal content"
    ),
    files: List[UploadFile] = File(None, description="PDF files to process"),
):
    """Create an expert witness persona and avatar image from case content or PDF files."""
    if create_avatar_image is None:
        raise HTTPException(
            status_code=500, detail="Avatar creation pipeline not available"
        )

    # Validate input - must have either text_query or files
    if not text_query and not files:
        raise HTTPException(
            status_code=400, detail="Must provide either text_query or PDF files"
        )

    # Process the request - returns both persona and image
    return await create_avatar_image(text_query=text_query, files=files)


@app.post("/api/persona")
async def create_persona_endpoint(
    text_query: Optional[str] = Form(
        None, description="Case description or legal content"
    ),
    files: List[UploadFile] = File(None, description="PDF files to process"),
):
    """Create just the expert witness persona from case content or PDF files (no image)."""
    if create_persona_only is None:
        raise HTTPException(
            status_code=500, detail="Persona creation pipeline not available"
        )

    # Validate input - must have either text_query or files
    if not text_query and not files:
        raise HTTPException(
            status_code=400, detail="Must provide either text_query or PDF files"
        )

    # Process the request - returns only persona
    return await create_persona_only(text_query=text_query, files=files)


####################################################################################################
# BACKWARD COMPATIBILITY - Legacy endpoints
####################################################################################################


@app.get("/avatar/status")
async def legacy_avatar_status():
    """Legacy endpoint - redirects to new structure."""
    return await pipeline_status()


@app.post("/api/create_avatar")
async def legacy_create_avatar(
    text_query: Optional[str] = Form(
        None, description="Case description or legal content"
    ),
    files: List[UploadFile] = File(None, description="PDF files to process"),
):
    """Legacy endpoint - redirects to new structure."""
    return await create_avatar_endpoint(text_query=text_query, files=files)
