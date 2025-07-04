"""
Image Generation Prompts

Simple prompts for generating professional expert witness avatar images.
"""

AVATAR_IMAGE_GENERATION_PROMPT = """
Professional headshot portrait of an expert witness:
- Business formal attire (suit or professional clothing)
- Confident and trustworthy expression
- Clean, neutral background
- Professional lighting
- Photorealistic style
- Age-appropriate for their experience level
- Suitable for legal proceedings
"""


def get_expert_image_prompt(expert_type="general", user_description=""):
    """
    Get image generation prompt for expert witness avatar.

    Args:
        expert_type (str): Type of expert (not used in simplified version)
        user_description (str): Additional user specifications

    Returns:
        str: Prompt for image generation
    """
    base_prompt = AVATAR_IMAGE_GENERATION_PROMPT

    if user_description:
        return f"{base_prompt}\n\nAdditional specifications: {user_description}"

    return base_prompt
