#!/usr/bin/env python3
"""
MCP Server for Agricultural Tools (Pests/Diseases and Government Schemes)
FastAPI Implementation - HTTP Transport with 2 Separate RAG API Endpoints
"""
import json
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import httpx
import os

# ============================================================================
# RAG API CONFIGURATION - 2 SEPARATE ENDPOINTS
# ============================================================================

# RAG API for Pests and Diseases
PESTS_DISEASES_RAG_URL = os.getenv(
    "PESTS_DISEASES_RAG_URL",
    "http://localhost:8001"
)

# RAG API for Government Schemes
GOVT_SCHEMES_RAG_URL = os.getenv(
    "GOVT_SCHEMES_RAG_URL",
    "http://localhost:8002"
)

RAG_TIMEOUT = int(os.getenv("RAG_TIMEOUT", "30"))  # seconds


# ============================================================================
# TOOL IMPLEMENTATIONS
# ============================================================================

async def query_pest_disease_rag(pest_name: str, crop: str = "General") -> dict:
    """Query separate Pests and Diseases RAG API"""
    print(f"🌾 Querying Pests/Diseases RAG API: pest={pest_name}, crop={crop}")
    try:
        async with httpx.AsyncClient(timeout=RAG_TIMEOUT) as client:
            # Make RAG API call to PESTS_DISEASES_RAG_URL
            response = await client.post(
                f"{PESTS_DISEASES_RAG_URL}/query",
                json={
                    "query": f"Tell me about {pest_name} pest/disease affecting {crop} crops. Include identification, symptoms, and management strategies.",
                    "context": "agricultural_pests_diseases",
                    "pest_name": pest_name,
                    "crop": crop
                }
            )
            
            if response.status_code == 200:
                rag_result = response.json()
                return {
                    "status": "success",
                    "pest_name": pest_name,
                    "crop": crop,
                    "information": rag_result.get("answer", "No information found"),
                    "sources": rag_result.get("sources", []),
                    "message": f"Information retrieved for {pest_name} from Pests & Diseases knowledge base"
                }
            else:
                return {
                    "status": "error",
                    "pest_name": pest_name,
                    "crop": crop,
                    "message": f"Pests/Diseases RAG API error: {response.status_code}",
                    "information": None
                }
    except httpx.TimeoutException:
        return {
            "status": "error",
            "pest_name": pest_name,
            "crop": crop,
            "message": "Pests/Diseases RAG API request timeout",
            "information": None
        }
    except Exception as e:
        return {
            "status": "error",
            "pest_name": pest_name,
            "crop": crop,
            "message": f"Pests/Diseases RAG API call error: {str(e)}",
            "information": None
        }


async def query_govt_scheme_rag(scheme_type: str, state: str = "All India") -> dict:
    """Query separate Government Schemes RAG API"""
    print(f"🏛️  Querying Government Schemes RAG API: scheme={scheme_type}, state={state}")
    try:
        async with httpx.AsyncClient(timeout=RAG_TIMEOUT) as client:
            # Make RAG API call to GOVT_SCHEMES_RAG_URL
            response = await client.post(
                f"{GOVT_SCHEMES_RAG_URL}/query",
                json={
                    "query": f"Tell me about {scheme_type} schemes in {state} for farmers. Include benefits, eligibility criteria, required documents, and processing time.",
                    "context": "agricultural_govt_schemes",
                    "scheme_type": scheme_type,
                    "state": state
                }
            )
            
            if response.status_code == 200:
                rag_result = response.json()
                return {
                    "status": "success",
                    "scheme_type": scheme_type,
                    "state": state,
                    "information": rag_result.get("answer", "No information found"),
                    "sources": rag_result.get("sources", []),
                    "message": f"Scheme information retrieved for {scheme_type} from Government Schemes knowledge base"
                }
            else:
                return {
                    "status": "error",
                    "scheme_type": scheme_type,
                    "state": state,
                    "message": f"Government Schemes RAG API error: {response.status_code}",
                    "information": None
                }
    except httpx.TimeoutException:
        return {
            "status": "error",
            "scheme_type": scheme_type,
            "state": state,
            "message": "Government Schemes RAG API request timeout",
            "information": None
        }
    except Exception as e:
        return {
            "status": "error",
            "scheme_type": scheme_type,
            "state": state,
            "message": f"Government Schemes RAG API call error: {str(e)}",
            "information": None
        }


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class ToolCallRequest(BaseModel):
    name: str
    arguments: Dict[str, Any]


# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(title="Agricultural MCP Server")


@app.post("/getToolsList")
async def list_tools():
    """List available tools"""
    print("📋 /getToolsList endpoint called")
    tools = {
        "tools": [
            {
                "name": "pests_and_diseases",
                "description": "Query the Pests and Diseases knowledge base. Get identification, symptoms, and management strategies for agricultural pests and diseases.",
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
                "description": "Query the Government Schemes knowledge base. Get information about agricultural subsidies, loans, and support schemes with eligibility criteria.",
                "inputSchema": {
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
            }
        ]
    }
    print(f"✅ Returning {len(tools['tools'])} tools")
    return tools


@app.post("/callTool")
async def call_tool(request: ToolCallRequest):
    """Execute a tool"""
    print(f"\n{'='*60}")
    print(f"🔧 /callTool endpoint called")
    print(f"{'='*60}")
    print(f"📝 Tool name: {request.name}")
    print(f"📝 Arguments: {request.arguments}")
    
    tool_name = request.name
    arguments = request.arguments
    
    if tool_name == "pests_and_diseases":
        pest_name = arguments.get("pest_name", "")
        crop = arguments.get("crop", "General")
        print(f"➡️  Calling pests_and_diseases with pest_name={pest_name}, crop={crop}")
        result = await query_pest_disease_rag(pest_name, crop)
        print(f"✅ Pest/Disease result: {result}")
        return {"result": result}
    
    elif tool_name == "govt_schemes":
        scheme_type = arguments.get("scheme_type", "")
        state = arguments.get("state", "All India")
        print(f"➡️  Calling govt_schemes with scheme_type={scheme_type}, state={state}")
        result = await query_govt_scheme_rag(scheme_type, state)
        print(f"✅ Scheme result: {result}")
        return {"result": result}
    
    else:
        print(f"❌ Unknown tool: {tool_name}")
        raise HTTPException(status_code=404, detail=f"Unknown tool: {tool_name}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🚀 Agricultural MCP Server - 2 Separate RAG Endpoints")
    print("=" * 70)
    print("\n📍 RAG API Configuration:")
    print(f"   Pests & Diseases RAG: {PESTS_DISEASES_RAG_URL}")
    print(f"   Government Schemes RAG: {GOVT_SCHEMES_RAG_URL}")
    print(f"   Timeout: {RAG_TIMEOUT} seconds")
    print("\n📋 Available Endpoints:")
    print("   POST /tools/list  - List available tools")
    print("   POST /tools/call  - Execute a tool")
    print("\n" + "=" * 70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8005)