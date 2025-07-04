"""
Gradio App for Expert Witness Avatar Creation

This app extracts text from PDF documents and generates expert witness personas
with avatar images using the Deposia API.
"""

import gradio as gr
import requests
import PyPDF2
import io
import base64
from PIL import Image
import json
from typing import Tuple, Optional

# Configuration
API_BASE_URL = (
    "https://vercel-deposia-git-main-abhipis-projects.vercel.app"  # Hosted Deposia API
)
AVATAR_ENDPOINT = f"{API_BASE_URL}/avatar/create-image"
STATUS_ENDPOINT = f"{API_BASE_URL}/avatar/status"


def extract_text_from_pdf(pdf_file) -> str:
    """
    Extract text content from a PDF file.

    Args:
        pdf_file: Uploaded PDF file object

    Returns:
        str: Extracted text content
    """
    try:
        # Read the PDF file
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text_content = ""

        # Extract text from all pages
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text_content += page.extract_text() + "\n"

        return text_content.strip()

    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"


def summarize_document_for_expert(text_content: str, max_length: int = 1000) -> str:
    """
    Create a summary of the document for expert witness generation.

    Args:
        text_content (str): Full text from the document
        max_length (int): Maximum length for the summary

    Returns:
        str: Summarized text suitable for expert witness creation
    """
    # If text is short enough, return as-is
    if len(text_content) <= max_length:
        return text_content

    # Simple truncation with attempt to end at sentence boundary
    truncated = text_content[:max_length]
    last_period = truncated.rfind(".")

    if last_period > max_length * 0.8:  # If we find a period in the last 20%
        return truncated[: last_period + 1]
    else:
        return truncated + "..."


def check_api_status() -> Tuple[bool, str]:
    """
    Check if the avatar creation API is available.

    Returns:
        Tuple[bool, str]: (is_available, status_message)
    """
    try:
        response = requests.get(STATUS_ENDPOINT, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, f"API Status: {data.get('message', 'OK')}"
        else:
            return False, f"API Error: Status {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"API Connection Error: {str(e)}"


def create_expert_witness_avatar(
    pdf_file, expert_type: str, custom_query: str = ""
) -> Tuple[str, Optional[Image.Image], str]:
    """
    Main function to create expert witness avatar from PDF document.

    Args:
        pdf_file: Uploaded PDF file
        expert_type (str): Type of expert witness
        custom_query (str): Optional custom query to append

    Returns:
        Tuple[str, Image, str]: (persona_text, avatar_image, status_message)
    """
    try:
        # Check API availability first
        api_available, status_msg = check_api_status()
        if not api_available:
            return "", None, f"❌ {status_msg}"

        # Extract text from PDF
        if pdf_file is None:
            return "", None, "❌ Please upload a PDF file"

        extracted_text = extract_text_from_pdf(pdf_file)

        if extracted_text.startswith("Error"):
            return "", None, f"❌ {extracted_text}"

        if not extracted_text.strip():
            return "", None, "❌ No text found in the PDF document"

        # Create query for expert witness generation
        summarized_text = summarize_document_for_expert(extracted_text)

        if custom_query:
            query = (
                f"{custom_query}\n\nBased on this document content:\n{summarized_text}"
            )
        else:
            query = f"Create an expert witness for a case involving this document:\n{summarized_text}"

        # Call the avatar creation API
        api_payload = {"text_query": query, "expert_type": expert_type}

        response = requests.post(
            AVATAR_ENDPOINT,
            json=api_payload,
            timeout=60,  # Generous timeout for AI generation
        )

        if response.status_code != 200:
            return "", None, f"❌ API Error: {response.status_code} - {response.text}"

        result = response.json()

        if result.get("status") != "ok":
            return "", None, f"❌ API Error: {result.get('message', 'Unknown error')}"

        data = result.get("data", {})
        persona = data.get("persona", "No persona generated")
        image_url = data.get("image_url")

        # Download and process the avatar image
        avatar_image = None
        if image_url:
            try:
                img_response = requests.get(image_url, timeout=30)
                if img_response.status_code == 200:
                    avatar_image = Image.open(io.BytesIO(img_response.content))
            except Exception as e:
                print(f"Error downloading image: {e}")

        success_msg = f"✅ Expert witness avatar created successfully! (ID: {data.get('avatar_id', 'N/A')})"
        return persona, avatar_image, success_msg

    except requests.exceptions.Timeout:
        return (
            "",
            None,
            "❌ Request timed out. The AI generation is taking longer than expected.",
        )
    except Exception as e:
        return "", None, f"❌ Unexpected error: {str(e)}"


def create_gradio_interface():
    """Create and configure the Gradio interface."""

    # Custom CSS for better styling
    css = """
    .container {
        max-width: 1200px;
        margin: auto;
    }
    .persona-output {
        max-height: 400px;
        overflow-y: auto;
        border: 1px solid #ddd;
        padding: 15px;
        border-radius: 8px;
        background-color: #f9f9f9;
    }
    .status-message {
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    """

    with gr.Blocks(css=css, title="Expert Witness Avatar Creator") as interface:
        gr.Markdown(
            """
            # 🎯 Expert Witness Avatar Creator
            
            Upload a PDF document and generate a professional expert witness persona with avatar image.
            Perfect for legal case preparation and deposition planning.
            """
        )

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📄 Document Upload")

                pdf_input = gr.File(
                    label="Upload PDF Document", file_types=[".pdf"], type="binary"
                )

                expert_type = gr.Dropdown(
                    choices=[
                        "general",
                        "technical",
                        "medical",
                        "financial",
                        "academic",
                    ],
                    value="general",
                    label="Expert Type",
                )

                custom_query = gr.Textbox(
                    label="Custom Instructions (Optional)",
                    placeholder="e.g., 'Need an expert in cybersecurity for data breach litigation'",
                    lines=3,
                )

                create_btn = gr.Button(
                    "🚀 Generate Expert Witness Avatar", variant="primary", size="lg"
                )

            with gr.Column(scale=2):
                gr.Markdown("### 👤 Generated Expert Witness")

                with gr.Row():
                    with gr.Column(scale=2):
                        persona_output = gr.Textbox(
                            label="Expert Witness Persona",
                            lines=15,
                            elem_classes=["persona-output"],
                        )

                    with gr.Column(scale=1):
                        avatar_image = gr.Image(label="Avatar Image", height=300)

                status_output = gr.Textbox(
                    label="Status", elem_classes=["status-message"]
                )

        # Event handlers
        create_btn.click(
            fn=create_expert_witness_avatar,
            inputs=[pdf_input, expert_type, custom_query],
            outputs=[persona_output, avatar_image, status_output],
        )

        # Example section
        gr.Markdown(
            """
            ### 📋 How to Use:
            
            1. **Upload PDF**: Choose a PDF document related to your legal case
            2. **Select Expert Type**: Choose the most appropriate expert category
            3. **Add Custom Instructions** (Optional): Provide specific requirements
            4. **Generate**: Click the button to create your expert witness persona and avatar
            
            ### 🎯 Expert Types:
            - **General**: Any field of expertise
            - **Technical**: Engineering, IT, cybersecurity, etc.
            - **Medical**: Healthcare, medical malpractice, etc.
            - **Financial**: Accounting, financial analysis, etc.
            - **Academic**: Research, education, scholarly expertise
            """
        )

    return interface


def main():
    """Launch the Gradio app."""
    interface = create_gradio_interface()

    # Launch with public sharing for easy access
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,  # Set to False for local only
        debug=True,
    )


if __name__ == "__main__":
    main()
