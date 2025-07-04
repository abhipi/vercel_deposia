"""
Prompts package for Deposia API

Simple prompts for expert witness avatar creation.
"""

# Import essential prompts only
from .expert_witness_prompts import (
    EXPERT_WITNESS_SYSTEM_PROMPT,
    EXPERT_WITNESS_USER_PROMPT_TEMPLATE,
)
from .image_generation_prompts import AVATAR_IMAGE_GENERATION_PROMPT

__all__ = [
    "EXPERT_WITNESS_SYSTEM_PROMPT",
    "EXPERT_WITNESS_USER_PROMPT_TEMPLATE",
    "AVATAR_IMAGE_GENERATION_PROMPT",
]
