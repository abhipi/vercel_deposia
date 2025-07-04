# Deposia Expert Witness Avatar Creator

A simplified AI-powered system for creating professional expert witness personas with avatar images from legal case content.

## Features

- **Simple PDF Upload**: Extract text from legal documents
- **Direct Text Input**: Enter case descriptions directly  
- **AI-Generated Personas**: Creates professional expert witness profiles using GPT-4o
- **Avatar Images**: Generates professional headshots using FLUX.1 via Together AI
- **REST API**: Hosted on Vercel for easy integration
- **Gradio Interface**: User-friendly web interface

## Quick Start

### 1. Environment Setup

You'll need API keys for:
- **OpenAI** (for GPT-4o text generation)
- **Together AI** (for FLUX.1 image generation)

Create a `.env` file:
```bash
OPENAI_API_KEY=your_openai_api_key_here
TOGETHER_API_KEY=your_together_ai_api_key_here
```

### 2. Install Dependencies

Using pipenv (recommended):
```bash
pipenv install
```

### 3. Run the Gradio Interface

```bash
pipenv run python launch_gradio.py
```

The interface will be available at `http://localhost:7860`

## API Usage

### Health Check
```bash
curl https://vercel-deposia.vercel.app/health
```

### Create Avatar
```bash
curl -X POST "https://vercel-deposia.vercel.app/api/create_avatar" \
  -H "Content-Type: application/json" \
  -d '{"text_query": "Medical malpractice case involving surgical error"}'
```

## Configuration

Edit `config.toml` to customize:

```toml
[openai]
chat_model = "gpt-4o"
max_tokens = 1000
temperature = 0.7

[together_ai]
image_model = "black-forest-labs/FLUX.1-kontext-dev"
max_tokens = 512
temperature = 0.7
```

## How It Works

1. **Input**: Upload PDF or enter case description
2. **Text Processing**: Extract and clean case content
3. **Persona Generation**: GPT-4o creates professional expert witness profile
4. **Avatar Creation**: FLUX.1 generates professional headshot image
5. **Output**: Complete expert witness package with persona and avatar

## API Endpoints

- `GET /health` - API health check
- `GET /avatar/status` - Avatar pipeline status  
- `POST /api/create_avatar` - Create expert witness avatar

### Request Format
```json
{
  "text_query": "Your case description here"
}
```

### Response Format
```json
{
  "status": "ok",
  "message": "Expert witness avatar created successfully",
  "data": {
    "persona": "Generated expert witness profile...",
    "image_url": "https://...",
    "avatar_id": "expert_1234",
    "models_used": {
      "chat": "gpt-4o",
      "image": "black-forest-labs/FLUX.1-kontext-dev"
    }
  }
}
```

## Technology Stack

- **FastAPI**: REST API framework
- **Gradio**: Web interface
- **OpenAI GPT-4o**: Text generation
- **Together AI FLUX.1**: Image generation
- **Vercel**: Hosting platform
- **Python 3.10+**: Runtime environment

## File Structure

```
vercel_deposia/
├── api/
│   └── server.py                 # FastAPI server
├── data/
│   └── avatar_creation_pipeline.py  # Core avatar creation logic
├── gradio_app.py                 # Gradio web interface
├── launch_gradio.py              # Interface launcher
├── config.toml                   # Configuration settings
├── Pipfile                       # Dependencies
└── README.md                     # This file
```

## Testing

Test the API locally:
```bash
pipenv run python test_api.py
```

Test with the hosted API:
```bash
curl https://vercel-deposia.vercel.app/health
```

## Environment Variables

Required:
- `OPENAI_API_KEY` - OpenAI API key for GPT-4o
- `TOGETHER_API_KEY` - Together AI API key for FLUX.1

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure both OpenAI and Together AI keys are set
2. **Dependency Issues**: Use `pipenv install` to ensure clean environment
3. **Network Timeouts**: Together AI image generation can take 30-60 seconds

### Debug Mode

Run with debug output:
```bash
PYTHONPATH=. pipenv run python gradio_app.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License. 