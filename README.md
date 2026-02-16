# Agricultural MCP Server

A FastAPI-based Model Context Protocol (MCP) server providing agricultural intelligence tools for pest/disease identification and government scheme information retrieval. Built with dual RAG (Retrieval-Augmented Generation) API endpoints for specialized knowledge domains.

## Overview

The Agricultural MCP Server acts as an intelligent intermediary connecting farmers and agricultural professionals with comprehensive knowledge about:

- **Pests & Diseases**: Identification, symptoms, and management strategies for agricultural pests and diseases
- **Government Schemes**: Agricultural subsidies, loans, insurance programs, and support schemes with eligibility criteria

The server uses separate RAG (Retrieval-Augmented Generation) APIs for each domain, ensuring specialized and accurate information retrieval.

## Features

- 🌾 **Dual-Domain Knowledge Base**: Separate RAG endpoints for pests/diseases and government schemes
- ⚡ **Asynchronous Processing**: Built with FastAPI for high-performance, non-blocking operations
- 🔌 **MCP Protocol Compatible**: Implements the Model Context Protocol for seamless integration
- 🌐 **HTTP REST API**: Clean, documented endpoints for tool discovery and execution
- ⏱️ **Configurable Timeouts**: Resilient error handling with customizable request timeouts
- 📊 **Comprehensive Logging**: Detailed console output for monitoring and debugging
- 🛡️ **Error Handling**: Graceful error responses with informative messages

## System Requirements

- Python 3.8+
- pip (Python package manager)

## Installation

### 1. Clone or Download the Repository

```bash
git clone <repository-url>
cd agricultural-mcp-server
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies:**
- `fastapi==0.104.1` - Modern web framework for building APIs
- `uvicorn==0.24.0` - ASGI server for running FastAPI applications
- `httpx==0.25.2` - Async HTTP client for RAG API communication
- `pydantic==2.5.0` - Data validation and settings management
- `python-multipart==0.0.6` - Support for multipart form data

## Configuration

### Environment Variables

Configure the server behavior using the following environment variables:

```bash
# Pests and Diseases RAG API endpoint
PESTS_DISEASES_RAG_URL=http://localhost:8001

# Government Schemes RAG API endpoint
GOVT_SCHEMES_RAG_URL=http://localhost:8002

# Request timeout in seconds
RAG_TIMEOUT=30
```

**Default Values:**
- `PESTS_DISEASES_RAG_URL`: `http://localhost:8001`
- `GOVT_SCHEMES_RAG_URL`: `http://localhost:8002`
- `RAG_TIMEOUT`: `30` seconds

### Example Configuration

```bash
export PESTS_DISEASES_RAG_URL=http://rag-service-1.example.com:8001
export GOVT_SCHEMES_RAG_URL=http://rag-service-2.example.com:8002
export RAG_TIMEOUT=45
```

## Running the Server

### Basic Usage

```bash
python mcp_server.py
```

The server will start on `http://0.0.0.0:8000` with the following message:

```
======================================================================
🚀 Agricultural MCP Server - 2 Separate RAG Endpoints
======================================================================

🔧 RAG API Configuration:
   Pests & Diseases RAG: http://localhost:8001
   Government Schemes RAG: http://localhost:8002
   Timeout: 30 seconds

📋 Available Endpoints:
   GET  /              - Root info endpoint
   GET  /health        - Health check
   POST /getToolsList  - List available tools
   POST /callTool      - Execute a tool

======================================================================
```

### With Uvicorn (Production)

```bash
uvicorn mcp_server:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Health & Information

#### `GET /`
Returns server information and available endpoints.

**Response:**
```json
{
  "status": "healthy",
  "service": "Agricultural MCP Server",
  "version": "1.0.0",
  "endpoints": {
    "health": "GET /health",
    "getToolsList": "POST /getToolsList",
    "callTool": "POST /callTool",
    "docs": "GET /docs (Swagger UI)"
  }
}
```

#### `GET /health`
Health check endpoint for monitoring and load balancing.

**Response:**
```json
{
  "status": "healthy",
  "service": "Agricultural MCP Server"
}
```

### Tools Management

#### `POST /getToolsList`
Retrieves the list of available tools with their descriptions and input schemas.

**Response:**
```json
{
  "tools": [
    {
      "name": "pests_and_diseases",
      "description": "Query the Pests and Diseases knowledge base...",
      "inputSchema": {
        "type": "object",
        "properties": {
          "pest_name": {
            "type": "string",
            "description": "Name of the pest or disease to query"
          },
          "crop": {
            "type": "string",
            "description": "Type of crop affected (optional)"
          }
        },
        "required": ["pest_name"]
      }
    },
    {
      "name": "govt_schemes",
      "description": "Query the Government Schemes knowledge base...",
      "inputSchema": {...}
    }
  ]
}
```

#### `POST /callTool`
Executes a specified tool with provided arguments.

**Request Body:**
```json
{
  "name": "pests_and_diseases",
  "arguments": {
    "pest_name": "Fall Armyworm",
    "crop": "Maize"
  }
}
```

**Response:**
```json
{
  "result": {
    "status": "success",
    "pest_name": "Fall Armyworm",
    "crop": "Maize",
    "information": "Fall Armyworm is a highly destructive pest...",
    "sources": ["document_1.pdf", "knowledge_base_2.txt"],
    "message": "Information retrieved for Fall Armyworm from Pests & Diseases knowledge base"
  }
}
```

## Tools Reference

### 1. Pests and Diseases Tool

**Name:** `pests_and_diseases`

**Description:** Query the Pests and Diseases knowledge base for identification, symptoms, and management strategies.

**Parameters:**
- `pest_name` (string, required): Name of the pest or disease
- `crop` (string, optional): Type of crop affected. Default: "General"

**Example Usage:**
```json
{
  "name": "pests_and_diseases",
  "arguments": {
    "pest_name": "Powdery Mildew",
    "crop": "Wheat"
  }
}
```

### 2. Government Schemes Tool

**Name:** `govt_schemes`

**Description:** Query the Government Schemes knowledge base for agricultural subsidies, loans, and support programs.

**Parameters:**
- `scheme_type` (string, required): Type of scheme (e.g., "subsidy", "loan", "insurance")
- `state` (string, optional): State or region for scheme eligibility. Default: "All India"

**Example Usage:**
```json
{
  "name": "govt_schemes",
  "arguments": {
    "scheme_type": "crop insurance",
    "state": "Maharashtra"
  }
}
```

## Interactive API Documentation

Once the server is running, access the interactive Swagger UI documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide interactive endpoints for testing all available tools and endpoints.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│         Client / MCP Integration Layer              │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│       Agricultural MCP Server (FastAPI)             │
│  ┌─────────────────────────────────────────────┐  │
│  │  /getToolsList  - Tool Discovery            │  │
│  │  /callTool      - Tool Execution            │  │
│  │  /health        - Health Check              │  │
│  └─────────────────────────────────────────────┘  │
└────────────────┬─────────────────────────────────┬─┘
                 │                                 │
        ┌────────▼────────┐         ┌──────────────▼────────┐
        │  Pests/Diseases │         │ Government Schemes    │
        │   RAG API       │         │     RAG API           │
        │  (localhost:    │         │   (localhost:         │
        │     8001)       │         │      8002)            │
        └─────────────────┘         └───────────────────────┘
```

## Error Handling

The server provides comprehensive error handling with informative responses:

### Timeout Error
```json
{
  "status": "error",
  "pest_name": "Example Pest",
  "crop": "Wheat",
  "message": "Pests/Diseases RAG API request timeout",
  "information": null
}
```

### RAG API Error
```json
{
  "status": "error",
  "pest_name": "Example Pest",
  "crop": "Wheat",
  "message": "Pests/Diseases RAG API error: 500",
  "information": null
}
```

### Unknown Tool
```
HTTP/1.1 404 Not Found
{
  "detail": "Unknown tool: invalid_tool_name"
}
```

## Logging

The server provides detailed console logging for debugging and monitoring:

```
============================================================
🚀 Agricultural MCP Server - 2 Separate RAG Endpoints
============================================================

🔧 RAG API Configuration:
   Pests & Diseases RAG: http://localhost:8001
   Government Schemes RAG: http://localhost:8002
   Timeout: 30 seconds

📋 Available Endpoints:
   GET  /              - Root info endpoint
   GET  /health        - Health check
   POST /getToolsList  - List available tools
   POST /callTool      - Execute a tool

============================================================

============================================================
🔧 /callTool endpoint called
============================================================
🔍 Tool name: pests_and_diseases
🔍 Arguments: {'pest_name': 'Fall Armyworm', 'crop': 'Maize'}
➡️  Calling pests_and_diseases with pest_name=Fall Armyworm, crop=Maize
✅ Pest/Disease result: {...}
```

## Development Guide

### Project Structure

```
agricultural-mcp-server/
├── mcp_server.py          # Main server application
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

### Code Organization

The `mcp_server.py` file is organized into sections:

1. **RAG API Configuration** - Environment variables and API endpoints
2. **Tool Implementations** - Query functions for RAG APIs
3. **Pydantic Models** - Request/response data validation
4. **FastAPI Application** - Endpoints and route handlers

### Adding New Tools

To add a new tool:

1. Create an async function following the naming pattern `query_*_rag()`
2. Add the tool definition to `/getToolsList` endpoint
3. Add a handler in `/callTool` endpoint
4. Update this README with tool documentation

### Testing Tools Locally

Using `curl`:

```bash
# List available tools
curl -X POST http://localhost:8000/getToolsList

# Call a tool
curl -X POST http://localhost:8000/callTool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "pests_and_diseases",
    "arguments": {
      "pest_name": "Fall Armyworm",
      "crop": "Maize"
    }
  }'
```

Using Python:

```python
import httpx
import asyncio

async def test():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/callTool",
            json={
                "name": "pests_and_diseases",
                "arguments": {
                    "pest_name": "Fall Armyworm",
                    "crop": "Maize"
                }
            }
        )
        print(response.json())

asyncio.run(test())
```

## Deployment

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mcp_server.py .

EXPOSE 8000

ENV PESTS_DISEASES_RAG_URL=http://rag-pests:8001
ENV GOVT_SCHEMES_RAG_URL=http://rag-schemes:8002
ENV RAG_TIMEOUT=30

CMD ["python", "mcp_server.py"]
```

Build and run:

```bash
docker build -t agricultural-mcp-server .
docker run -p 8000:8000 agricultural-mcp-server
```

### Kubernetes Deployment

Example manifest:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: agricultural-mcp-server
spec:
  selector:
    app: agricultural-mcp-server
  ports:
    - protocol: TCP
      port: 8000
      targetPort: 8000
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agricultural-mcp-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agricultural-mcp-server
  template:
    metadata:
      labels:
        app: agricultural-mcp-server
    spec:
      containers:
      - name: mcp-server
        image: agricultural-mcp-server:latest
        ports:
        - containerPort: 8000
        env:
        - name: PESTS_DISEASES_RAG_URL
          value: http://rag-pests-service:8001
        - name: GOVT_SCHEMES_RAG_URL
          value: http://rag-schemes-service:8002
        - name: RAG_TIMEOUT
          value: "30"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
```

## Troubleshooting

### Server won't start

**Issue**: `Address already in use`

**Solution**:
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### RAG API Connection Errors

**Issue**: `Pests/Diseases RAG API request timeout`

**Solution**:
- Verify RAG APIs are running on configured addresses
- Check network connectivity between services
- Increase `RAG_TIMEOUT` if APIs are slow

```bash
export RAG_TIMEOUT=60
python mcp_server.py
```

### CORS Issues

If integrating with a frontend, add CORS middleware:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Performance Optimization

### Enable Uvicorn Workers

For production, run with multiple worker processes:

```bash
uvicorn mcp_server:app --host 0.0.0.0 --port 8000 --workers 4
```

### Configure RAG API Pooling

Adjust `RAG_TIMEOUT` based on RAG API performance:

```bash
export RAG_TIMEOUT=45  # Increase if RAG APIs are slower
```

## Contributing

Guidelines for contributions:

1. Maintain the existing code structure
2. Add detailed docstrings to new functions
3. Update this README with new features
4. Test locally before submitting changes
5. Follow PEP 8 style guidelines












### Version 1.0.0 (Release)
- Initial release
- Dual RAG API endpoints for pests/diseases and government schemes
- FastAPI HTTP transport implementation
- Comprehensive error handling and logging
- Full MCP protocol support

