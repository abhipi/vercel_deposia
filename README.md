# Deposia Expert Witness Avatar Creator

A simplified AI-powered system for creating expert witness personas with avatar images from legal case content. Supports both text queries and PDF file uploads.

## Features

- **Text Input**: Create expert witness personas from text descriptions
- **PDF Upload**: Upload one or multiple PDF files containing legal case content
- **AI-Powered**: Uses OpenAI GPT-4o for persona generation and Together AI FLUX.1-schnell for avatar images
- **Simple API**: Only 3 endpoints for maximum simplicity

## API Endpoints

### 1. Health Check
```
GET /health
```
Returns server health status.

### 2. Avatar Status
```
GET /avatar/status
```
Returns the status of the avatar creation pipeline.

### 3. Create Avatar
```
POST /api/create_avatar
```
Create an expert witness persona and avatar from case content.

**Input Options:**

**Option 1: Text Query**
```bash
curl -X POST "http://localhost:8000/api/create_avatar" \
  -F "text_query=Construction defect case requiring structural engineering expert witness"
```

**Option 2: PDF Upload**
```bash
curl -X POST "http://localhost:8000/api/create_avatar" \
  -F "files=@case_document.pdf"
```

**Option 3: Multiple PDFs**
```bash
curl -X POST "http://localhost:8000/api/create_avatar" \
  -F "files=@case_summary.pdf" \
  -F "files=@expert_requirements.pdf"
```

**Option 4: Text + PDFs**
```bash
curl -X POST "http://localhost:8000/api/create_avatar" \
  -F "text_query=Additional context about the case" \
  -F "files=@case_document.pdf"
```

## Response Format

```json
{
  "status": "ok",
  "message": "Expert witness avatar created successfully from 2 PDF file(s)",
  "data": {
    "persona": "Generated expert witness profile...",
    "image_url": "https://...",
    "avatar_id": "expert_1234",
    "query": "Original query or PDF content",
    "files_processed": ["case_summary.pdf", "expert_requirements.pdf"],
    "models_used": {
      "chat": "gpt-4o", 
      "image": "black-forest-labs/FLUX.1-schnell"
    }
  }
}
```

## Setup

1. **Install Dependencies**
   ```bash
   pipenv install
   pipenv install --dev  # For testing
   ```

2. **Environment Variables**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   export TOGETHER_API_KEY="your-together-ai-api-key"
   ```

3. **Run the Server**
   ```bash
   pipenv run uvicorn api.server:app --host 0.0.0.0 --port 8000
   ```

## Testing

Run the comprehensive test suite:
```bash
pipenv run python test_api.py
```

The test suite includes:
- Health check
- Avatar status
- Text-based avatar creation
- Single PDF upload
- Multiple PDF uploads

## PDF Support

The system supports PDF text extraction using PyPDF2. It will:
- Extract text from all pages in each PDF
- Combine content from multiple PDFs
- Include filename headers for organization
- Handle PDF processing errors gracefully

**Supported file types:** `.pdf` only

## Configuration

Edit `config.toml` to customize model settings:

```toml
[openai]
chat_model = "gpt-4o"
max_tokens = 1000
temperature = 0.7

[together_ai]
image_model = "black-forest-labs/FLUX.1-schnell"
max_tokens = 512
temperature = 0.7
```

## Deployment

Deploy to Vercel using the included `vercel.json` configuration.

## Architecture

- **FastAPI Backend**: Handles API requests and file uploads
- **OpenAI GPT-4o**: Generates expert witness personas
- **Together AI FLUX.1**: Creates professional avatar images
- **PyPDF2**: Extracts text content from PDF files
- **Simple Design**: Focused on core functionality only 