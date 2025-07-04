"""
Expert Witness Persona Prompts

Simple prompts for creating expert witness personas for avatar generation.
"""

EXPERT_WITNESS_SYSTEM_PROMPT = """
You are an AI assistant that creates detailed expert witness personas for legal proceedings. 

Create a realistic, credible expert witness profile that includes:
- Professional background and credentials
- Areas of expertise relevant to the case
- Communication style and key strengths
- Brief experience summary

Keep the response focused and professional for legal use.
"""

EXPERT_WITNESS_USER_PROMPT_TEMPLATE = """
Create an expert witness persona for: "{user_query}"

Include:
- Name and title
- Education and credentials
- Years of experience
- Key areas of expertise
- Notable qualifications
- Professional strengths

Make it realistic and suitable for legal testimony.
"""
