"""
A simplified FastAPI server with health check endpoint.
Maintains the ability to dynamically import functions from the data folder.
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
        required_attrs=["get_avatar_status"],
    )
    get_avatar_status = avatar_pipeline.get_avatar_status
    create_avatar = avatar_pipeline.create_avatar
    validate_avatar_config = avatar_pipeline.validate_avatar_config
except (FileNotFoundError, ImportError, AttributeError) as e:
    logger.warning(f"Could not import avatar pipeline: {e}")
    get_avatar_status = None
    create_avatar = None
    validate_avatar_config = None

####################################################################################################
# FASTAPI APP
####################################################################################################
app = FastAPI(title="Simplified API Server", version="1.0.0")

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
# HEALTH CHECK ENDPOINTS
####################################################################################################
@app.get("/")
def read_root():
    """Root endpoint for basic health check."""
    return {"status": "ok", "message": "Server is running"}


@app.get("/health")
def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "ok",
        "message": "Server is healthy",
        "data_folder_exists": os.path.exists(DATA_FOLDER),
        "temp_dir_exists": os.path.exists(TEMP_DIR),
    }


####################################################################################################
# AVATAR CREATION ENDPOINTS
####################################################################################################
@app.get("/avatar/status")
async def avatar_status():
    """Get the status of the avatar creation pipeline."""
    if get_avatar_status is None:
        raise HTTPException(status_code=500, detail="Avatar pipeline not available")

    return get_avatar_status()


@app.post("/avatar/create")
async def create_avatar_endpoint(avatar_config: dict = None):
    """Create a new avatar with the given configuration."""
    if create_avatar is None:
        raise HTTPException(status_code=500, detail="Avatar creation not available")

    return create_avatar(avatar_config)


@app.post("/avatar/validate")
async def validate_config_endpoint(config: dict):
    """Validate an avatar configuration."""
    if validate_avatar_config is None:
        raise HTTPException(status_code=500, detail="Avatar validation not available")

    return validate_avatar_config(config)


####################################################################################################
# EXAMPLE: HOW TO USE DYNAMIC IMPORTS (COMMENTED OUT)
####################################################################################################
# Example of how to dynamically import and use functions from the data folder:
#
# try:
#     # Import a module from the data folder
#     example_module = dynamic_import(
#         module_path=os.path.join(DATA_FOLDER, "example_module.py"),
#         module_name="example_module",
#         required_attrs=["example_function"]
#     )
#     example_function = example_module.example_function
# except (FileNotFoundError, ImportError, AttributeError) as e:
#     logger.warning(f"Could not import example module: {e}")
#     example_function = None
#
# @app.post("/example")
# async def example_endpoint():
#     if example_function is None:
#         raise HTTPException(status_code=500, detail="Example function not available")
#
#     result = example_function()
#     return {"result": result}

# Uncomment and modify the above example to add your own endpoints that use data folder functions
