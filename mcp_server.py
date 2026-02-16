#!/usr/bin/env python3
"""
MCP Server for Agricultural Tools (Pests/Diseases and Government Schemes)
Proper MCP Implementation - Using Official MCP SDK v1.26.0 with HTTP Transport

This uses the official mcp package from Anthropic with HTTP transport,
keeping all original RAG API logic intact.
"""

import json
import logging
from typing import Any
import httpx
import os
import asyncio

from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.types as types

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# RAG API CONFIGURATION - 2 SEPARATE ENDPOINTS
# ============================================================================

PESTS_DISEASES_RAG_URL = os.getenv(
    "PESTS_DISEASES_RAG_URL",
    "https://agrigpt-backend-rag-pest-and-disease.onrender.com"
)

GOVT_SCHEMES_RAG_URL = os.getenv(
    "GOVT_SCHEMES_RAG_URL",
    "https://agrigpt-backend-rag-government-schemes-1.onrender.com"
)

RAG_TIMEOUT = int(os.getenv("RAG_TIMEOUT", "30"))  # seconds

logger.info(f"Pests & Diseases RAG URL: {PESTS_DISEASES_RAG_URL}")
logger.info(f"Government Schemes RAG URL: {GOVT_SCHEMES_RAG_URL}")
logger.info(f"RAG Timeout: {RAG_TIMEOUT} seconds")

# ============================================================================
# TOOL IMPLEMENTATIONS (SAME AS ORIGINAL)
# ============================================================================

async def query_pest_disease_rag(pest_name: str, crop: str = "General") -> dict:
    """Query Pests and Diseases RAG API from Render"""
    logger.info(f"🌾 Querying Pests/Diseases RAG API: pest={pest_name}, crop={crop}")
    
    try:
        async with httpx.AsyncClient(timeout=RAG_TIMEOUT) as client:
            # Build the question
            question_text = f"{pest_name} affecting {crop} crops" if crop and crop != "General" else pest_name
            
            logger.info(f"📤 Sending question: {question_text}")
            response = await client.post(
                f"{PESTS_DISEASES_RAG_URL}/query",
                json={
                    "question": question_text,
                    "top_k": 5
                }
            )
            logger.info(f"📥 Response status: {response.status_code}")
            
            if response.status_code == 200:
                rag_result = response.json()
                answer = rag_result.get("answer", "No information found")
                sources = rag_result.get("sources", [])
                
                # Extract just filenames from sources for cleaner display
                source_files = []
                if sources:
                    source_files = list(set([s.get("filename", "Unknown") for s in sources if isinstance(s, dict)]))
                
                return {
                    "status": "success",
                    "pest_name": pest_name,
                    "crop": crop,
                    "information": answer,
                    "sources": source_files,
                    "source_details": sources,
                    "message": f"Information retrieved for {pest_name} from Pests & Diseases RAG API"
                }
            else:
                error_detail = response.text
                logger.error(f"❌ RAG API Error {response.status_code}: {error_detail}")
                return {
                    "status": "error",
                    "pest_name": pest_name,
                    "crop": crop,
                    "message": f"Pests/Diseases RAG API error: {response.status_code}",
                    "error_detail": error_detail[:500],
                    "information": None
                }
    except httpx.TimeoutException:
        logger.error("Pests/Diseases RAG API request timeout")
        return {
            "status": "error",
            "pest_name": pest_name,
            "crop": crop,
            "message": "Pests/Diseases RAG API request timeout",
            "information": None
        }
    except Exception as e:
        logger.error(f"Pests/Diseases RAG API call error: {str(e)}")
        return {
            "status": "error",
            "pest_name": pest_name,
            "crop": crop,
            "message": f"Pests/Diseases RAG API call error: {str(e)}",
            "information": None
        }


async def query_govt_scheme_rag(scheme_type: str, state: str = "All India") -> dict:
    """Query Government Schemes RAG API from Render"""
    logger.info(f"🏛️  Querying Government Schemes RAG API: scheme={scheme_type}, state={state}")
    
    try:
        async with httpx.AsyncClient(timeout=RAG_TIMEOUT) as client:
            # Build the question
            if state and state != "All India":
                question_text = f"tell me the schemes related to {scheme_type} in {state}"
            else:
                question_text = f"tell me the schemes related to {scheme_type}"
            
            logger.info(f"📤 Sending question: {question_text}")
            response = await client.post(
                f"{GOVT_SCHEMES_RAG_URL}/query",
                json={
                    "question": question_text,
                    "top_k": 5
                }
            )
            logger.info(f"📥 Response status: {response.status_code}")
            
            if response.status_code == 200:
                rag_result = response.json()
                answer = rag_result.get("answer", "No information found")
                sources = rag_result.get("sources", [])
                
                # Extract just filenames from sources for cleaner display
                source_files = []
                if sources:
                    source_files = list(set([s.get("filename", "Unknown") for s in sources if isinstance(s, dict)]))
                
                return {
                    "status": "success",
                    "scheme_type": scheme_type,
                    "state": state,
                    "information": answer,
                    "sources": source_files,
                    "source_details": sources,
                    "message": f"Scheme information retrieved for {scheme_type} from Government Schemes RAG API"
                }
            else:
                error_detail = response.text
                logger.error(f"❌ RAG API Error {response.status_code}: {error_detail}")
                return {
                    "status": "error",
                    "scheme_type": scheme_type,
                    "state": state,
                    "message": f"Government Schemes RAG API error: {response.status_code}",
                    "error_detail": error_detail[:500],
                    "information": None
                }
    except httpx.TimeoutException:
        logger.error("Government Schemes RAG API request timeout")
        return {
            "status": "error",
            "scheme_type": scheme_type,
            "state": state,
            "message": "Government Schemes RAG API request timeout",
            "information": None
        }
    except Exception as e:
        logger.error(f"Government Schemes RAG API call error: {str(e)}")
        return {
            "status": "error",
            "scheme_type": scheme_type,
            "state": state,
            "message": f"Government Schemes RAG API call error: {str(e)}",
            "information": None
        }


# ============================================================================
# MCP SERVER SETUP (MCP SDK v1.26.0)
# ============================================================================

# Create the MCP server instance
server = Server("agricultural-mcp-server")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    logger.info("📋 Listing available tools")
    return [
        Tool(
            name="pests_and_diseases",
            description="Query the Pests and Diseases knowledge base. Get identification, symptoms, and management strategies for agricultural pests and diseases.",
            inputSchema={
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
        ),
        Tool(
            name="govt_schemes",
            description="Query the Government Schemes knowledge base. Get information about agricultural subsidies, loans, and support schemes with eligibility criteria.",
            inputSchema={
                "type": "object",
                "properties": {
                    "scheme_type": {
                        "type": "string",
                        "description": "Type of scheme: subsidy, loan, or insurance"
                    },
                    "state": {
                        "type": "string",
                        "description": "State or region for scheme eligibility (optional)"
                    }
                },
                "required": ["scheme_type"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a tool"""
    logger.info(f"🔨 Calling tool: {name} with arguments: {arguments}")
    
    if name == "pests_and_diseases":
        pest_name = arguments.get("pest_name", "")
        crop = arguments.get("crop", "General")
        
        if not pest_name:
            raise ValueError("pest_name is required")
        
        logger.info(f"➡️  Calling pests_and_diseases with pest_name={pest_name}, crop={crop}")
        result = await query_pest_disease_rag(pest_name, crop)
        logger.info(f"✅ Tool result: {result}")
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "govt_schemes":
        scheme_type = arguments.get("scheme_type", "")
        state = arguments.get("state", "All India")
        
        if not scheme_type:
            raise ValueError("scheme_type is required")
        
        logger.info(f"➡️  Calling govt_schemes with scheme_type={scheme_type}, state={state}")
        result = await query_govt_scheme_rag(scheme_type, state)
        logger.info(f"✅ Tool result: {result}")
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    else:
        raise ValueError(f"Unknown tool: {name}")


# ============================================================================
# HTTP SERVER ADAPTER (for HTTP transport)
# ============================================================================

from fastapi import FastAPI, Request
import uvicorn

app = FastAPI(
    title="Agricultural MCP Server",
    description="Proper MCP Server with Official SDK v1.26.0 - HTTP Transport"
)


@app.get("/")
async def root():
    """Root endpoint - for health checks and info"""
    return {
        "status": "healthy",
        "service": "Agricultural MCP Server (Official MCP SDK v1.26.0)",
        "version": "1.0.0",
        "transport": "HTTP",
        "info": "This is a proper MCP server using the official mcp SDK. Send JSON-RPC 2.0 requests to the root POST endpoint."
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Agricultural MCP Server"
    }


@app.post("/")
async def handle_json_rpc(request: Request):
    """
    Main JSON-RPC 2.0 endpoint for MCP protocol.
    This endpoint handles all MCP method calls using the official SDK.
    """
    try:
        body = await request.json()
        logger.info(f"📥 Received JSON-RPC request: {body}")
        
        if not isinstance(body, dict):
            return {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error"}
            }
        
        jsonrpc_version = body.get("jsonrpc")
        request_id = body.get("id")
        method = body.get("method")
        params = body.get("params", {})
        
        if jsonrpc_version != "2.0":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32600, "message": "Invalid Request: jsonrpc must be 2.0"}
            }
        
        if not method:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32600, "message": "Invalid Request: method is required"}
            }
        
        # Handle MCP protocol methods
        if method == "initialize":
            logger.info("🔧 Handling initialize request")
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "agricultural-mcp-server",
                    "version": "1.0.0"
                }
            }
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
        
        elif method == "tools/list":
            logger.info("📋 Handling tools/list request")
            tools_list = await list_tools()
            tools_data = []
            for tool in tools_list:
                tools_data.append({
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                })
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"tools": tools_data}
            }
        
        elif method == "tools/call":
            logger.info("🔨 Handling tools/call request")
            try:
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if not tool_name:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32602, "message": "Invalid params: name is required"}
                    }
                
                result = await call_tool(tool_name, arguments)
                
                # Convert TextContent objects to dictionaries
                result_list = []
                for item in result:
                    if isinstance(item, TextContent):
                        result_list.append({
                            "type": item.type,
                            "text": item.text
                        })
                    else:
                        result_list.append(item)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result_list
                }
            
            except ValueError as ve:
                if "required" in str(ve):
                    error_code = -32602
                else:
                    error_code = -32601
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": error_code, "message": str(ve)}
                }
            except Exception as e:
                logger.error(f"Tool call error: {str(e)}")
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
                }
        
        else:
            logger.warning(f"❌ Unknown method: {method}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            }
    
    except json.JSONDecodeError:
        logger.error("JSON decode error")
        return {
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32700, "message": "Parse error"}
        }
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32603, "message": "Internal error", "data": str(e)}
        }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🚀 Agricultural MCP Server - Official MCP SDK v1.26.0 Implementation")
    print("=" * 80)
    print("\n📍 RAG API Configuration:")
    print(f"   Pests & Diseases RAG: {PESTS_DISEASES_RAG_URL}")
    print(f"   Government Schemes RAG: {GOVT_SCHEMES_RAG_URL}")
    print(f"   Timeout: {RAG_TIMEOUT} seconds")
    print("\n📋 MCP Server Info:")
    print("   Server Name: agricultural-mcp-server")
    print("\n✅ Available Tools:")
    print("   1. pests_and_diseases - Query pest and disease information")
    print("   2. govt_schemes - Query government schemes information")
    print("\n" + "=" * 80 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8005)