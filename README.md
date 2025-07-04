# Deposia API Deployment

This is the deployment repository for **Deposia's API calls**, providing a streamlined FastAPI server optimized for Vercel deployment.

## Overview

Deposia API serves as the backend infrastructure for Deposia's core functionalities, including avatar creation pipelines and various data processing services. This deployment is designed to be lightweight, scalable, and easily maintainable.

## Architecture

```
vercel_deposia/
├── api/
│   └── server.py           # Main FastAPI application
├── data/
│   ├── avatar_creation_pipeline.py  # Avatar processing functions
│   └── prompts/            # Expert witness and image generation prompts
├── gradio_app.py           # Gradio interface for PDF processing
├── launch_gradio.py        # Gradio app launcher script
├── config.toml             # Configuration file for OpenAI and API settings
├── Pipfile                 # Python dependencies
├── vercel.json            # Vercel deployment configuration
└── README.md              # This file
```

## Features

- **Health Check Endpoints**: Basic server monitoring and status verification
- **Avatar Creation Pipeline**: Complete avatar processing and management system
- **Dynamic Module Loading**: Flexible import system for data folder functions
- **CORS Support**: Cross-origin resource sharing enabled
- **Vercel Optimized**: Configured for seamless Vercel deployment
- **Gradio Interface**: User-friendly web interface for PDF document processing
- **PDF Text Extraction**: Automatic text extraction from PDF documents
- **Expert Witness Generation**: AI-powered expert witness persona creation

## API Endpoints

### Health & Status
- `GET /` - Basic health check
- `GET /health` - Detailed server health information

### Avatar Management
- `GET /avatar/status` - Avatar pipeline status
- `POST /avatar/create-image` - Create expert witness persona and avatar image using OpenAI

## Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   # or using pipenv
   pipenv install
   ```

2. **Set up environment:**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   ```

3. **Run the server:**
   ```bash
   uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Create an expert witness avatar:**
   ```bash
   curl -X POST "http://localhost:8000/avatar/create-image" \
     -H "Content-Type: application/json" \
     -d '{
       "text_query": "Need a cybersecurity expert for a data breach case",
       "expert_type": "technical"
     }'
   ```

### Response Format

The API returns:
```json
{
  "status": "ok",
  "message": "Expert witness avatar created successfully",
  "data": {
    "persona": "Detailed expert witness profile...",
    "image_url": "https://generated-image-url.com/image.png",
    "expert_type": "technical",
    "query": "Need a cybersecurity expert for a data breach case",
    "avatar_id": "expert_1234"
  }
}
```

### Vercel Deployment

This repository is configured for automatic Vercel deployment. The `vercel.json` file contains the necessary configuration for serverless deployment.

## Gradio App - PDF Document Processing

For easy document processing, use the included Gradio web interface:

### Launch the Gradio App

1. **Start the API server** (in one terminal):
   ```bash
   uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Launch the Gradio interface** (in another terminal):
   ```bash
   python launch_gradio.py
   ```

3. **Access the interface**:
   - Local: `http://localhost:7860`
   - Public URL will be displayed in the terminal

### Using the Gradio Interface

1. **Upload PDF**: Select a PDF document related to your legal case
2. **Choose Expert Type**: Select from general, technical, medical, financial, or academic
3. **Add Custom Instructions**: Optionally provide specific requirements
4. **Generate Avatar**: Click to create expert witness persona and professional headshot

### Example Workflow

```
PDF Document → Text Extraction → Expert Persona Generation → Avatar Image Creation
```

The interface will display:
- **Expert Witness Persona**: Detailed professional profile
- **Avatar Image**: Professional headshot suitable for legal proceedings
- **Status Updates**: Real-time feedback on the generation process

## Configuration

- **Environment Variables**: Configure via `.env` file or Vercel environment settings
  - `OPENAI_API_KEY`: Required for avatar image generation and persona creation
- **Configuration File**: `config.toml` contains OpenAI model settings and API parameters
  - `chat_model`: OpenAI chat model (default: "gpt-4o")
  - `image_model`: OpenAI image generation model (default: "dall-e-3")
  - `max_tokens`: Maximum tokens for chat responses (default: 1500)
  - `temperature`: Creativity level for responses (default: 0.7)
- **CORS**: Currently set to allow all origins (`*`) - update for production
- **Logging**: Configured to suppress excessive HTTP client logs

## Data Folder Functions

The `data/` folder contains modular functions that are dynamically imported by the server:

- **avatar_creation_pipeline.py**: Expert witness avatar creation using OpenAI API
- **prompts/**: Simple, focused prompts for avatar creation
  - `expert_witness_prompts.py`: Core prompts for creating expert witness personas
  - `image_generation_prompts.py`: DALL-E prompts for professional headshots
- Add new modules to extend functionality

## Development

### Adding New Endpoints

1. Create your function in a new file within the `data/` folder
2. Use the `dynamic_import()` utility in `server.py` to import your module
3. Create new FastAPI endpoints that use your imported functions
4. Follow the existing pattern for error handling

### Example:
```python
# In data/my_new_module.py
def my_function():
    return {"status": "ok", "message": "Function working"}

# In api/server.py
my_module = dynamic_import("data/my_new_module.py", "my_module", ["my_function"])
my_function = my_module.my_function

@app.get("/my-endpoint")
async def my_endpoint():
    return my_function()
```

## Contributing

1. Follow the existing code structure and patterns
2. Add appropriate error handling for all new functions
3. Update this README when adding new major features
4. Test locally before deploying

## Support

For issues related to Deposia API deployment, please contact the development team or create an issue in the main Deposia repository.

---

**Deposia** - Revolutionizing avatar creation and digital interaction 