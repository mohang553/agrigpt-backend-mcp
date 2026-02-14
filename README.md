# agrigpt-backend-mcp
This is the repository containing the MCP code for the AgriGPT project



# Agricultural MCP Server

A FastAPI-based Model Context Protocol (MCP) server providing comprehensive agricultural tools for pest and disease management, as well as government scheme information.

## Overview

The Agricultural MCP Server is a RESTful API service designed to deliver agricultural knowledge and support resources. It exposes two primary knowledge bases through a standardized tool interface, enabling seamless integration with AI models and agricultural applications.

## Features

- **Pest and Disease Management**: Query a comprehensive knowledge base for identification, symptom recognition, and management strategies for agricultural pests and diseases
- **Government Schemes**: Access detailed information about agricultural subsidies, loans, and support schemes with eligibility criteria
- **Health Monitoring**: Built-in health check endpoint for service status verification
- **Professional Logging**: Structured logging for debugging and monitoring
- **RESTful Architecture**: Clean API design following REST conventions

## Requirements

- Python 3.8 or higher
- FastAPI 0.104.1
- Uvicorn 0.24.0
- httpx 0.25.2
- Pydantic 2.5.0
- python-multipart 0.0.6

## Installation

1. **Clone or download the repository**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**
   ```bash
   python mcp_server.py
   ```

## Configuration

The server runs with the following default configuration:

- **Host**: 0.0.0.0 (accessible from all network interfaces)
- **Port**: 8005
- **Log Level**: INFO

To modify these settings, edit the `uvicorn.run()` call in the `__main__` block of `mcp_server.py`.

## API Endpoints

### Health Check
**Endpoint**: `GET /`

Returns the current status of the server.

**Response**:
```json
{
  "status": "running",
  "service": "Agricultural MCP Server",
  "version": "1.0.0"
}
```

### List Available Tools
**Endpoint**: `POST /tools/list`

Retrieves a list of all available tools and their descriptions.

**Response**:
```json
{
  "tools": [
    {
      "name": "pests_and_diseases",
      "description": "Query the Pests and Diseases knowledge base. Get identification, symptoms, and management strategies for agricultural pests and diseases."
    },
    {
      "name": "govt_schemes",
      "description": "Query the Government Schemes knowledge base. Get information about agricultural subsidies, loans, and support schemes with eligibility criteria."
    }
  ]
}
```

## Available Tools

### 1. Pests and Diseases
Provides comprehensive information for agricultural pest and disease management:
- Pest and disease identification
- Symptom recognition and diagnosis
- Proven management strategies
- Prevention and control measures

### 2. Government Schemes
Delivers details on agricultural support programs:
- Subsidy information
- Loan schemes and terms
- Support program eligibility criteria
- Application procedures

## Usage

### Starting the Server

```bash
python mcp_server.py
```

The server will initialize and display available endpoints and tools:

```
======================================================================
🚀 Starting Agricultural MCP Server
======================================================================

📍 Available Endpoints:
   GET  /              - Health check
   POST /tools/list    - List available tools

📋 Available Tools:
   1. pests_and_diseases
   2. govt_schemes

======================================================================
```

### Example Requests

**Check server health**:
```bash
curl http://localhost:8005/
```

**List available tools**:
```bash
curl -X POST http://localhost:8005/tools/list
```

## Logging

The server implements structured logging to help with debugging and monitoring:

- **Log Format**: `TIMESTAMP - LEVEL - MESSAGE`
- **Log Level**: INFO (configurable via `logging.basicConfig()`)
- All API requests and responses are logged automatically

## Architecture

The server follows the MCP specification, providing a standardized interface for agricultural knowledge bases. The modular design allows for easy extension with additional tools and knowledge bases.

## Development

To extend the server with additional tools:

1. Add the tool definition to the `list_tools()` function
2. Implement the corresponding tool handler endpoint
3. Update logging as needed
4. Test with appropriate API calls

## Troubleshooting

**Port already in use**: If port 8005 is already in use, modify the port number in the `uvicorn.run()` call

**Connection issues**: Ensure the server is running and accessible at `http://localhost:8005`

**Missing dependencies**: Run `pip install -r requirements.txt` to ensure all packages are installed

## Support

For issues or feature requests, please refer to the project documentation or contact the development team.

## Version

Current Version: 1.0.0

## License

[Add appropriate license information here]