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
│   └── avatar_creation_pipeline.py  # Avatar processing functions
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

## API Endpoints

### Health & Status
- `GET /` - Basic health check
- `GET /health` - Detailed server health information

### Avatar Management
- `GET /avatar/status` - Avatar pipeline status
- `POST /avatar/create` - Create new avatar with configuration
- `POST /avatar/validate` - Validate avatar configuration

## Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   # or using pipenv
   pipenv install
   ```

2. **Run the server:**
   ```bash
   uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Access the API:**
   - Server: `http://localhost:8000`
   - Health check: `http://localhost:8000/health`
   - Avatar status: `http://localhost:8000/avatar/status`

### Vercel Deployment

This repository is configured for automatic Vercel deployment. The `vercel.json` file contains the necessary configuration for serverless deployment.

## Configuration

- **Environment Variables**: Configure via `.env` file or Vercel environment settings
- **CORS**: Currently set to allow all origins (`*`) - update for production
- **Logging**: Configured to suppress excessive HTTP client logs

## Data Folder Functions

The `data/` folder contains modular functions that are dynamically imported by the server:

- **avatar_creation_pipeline.py**: Avatar processing, validation, and creation functions
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