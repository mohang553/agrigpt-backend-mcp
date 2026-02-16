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

# RAG API for Pests and Diseases (Render)
PESTS_DISEASES_RAG_URL = os.getenv(
    "PESTS_DISEASES_RAG_URL",
    "https://agrigpt-backend-rag-pest-and-disease.onrender.com"
)

# RAG API for Government Schemes (Render)
GOVT_SCHEMES_RAG_URL = os.getenv(
    "GOVT_SCHEMES_RAG_URL",
    "https://agrigpt-backend-rag-government-schemes-1.onrender.com"
)

RAG_TIMEOUT = int(os.getenv("RAG_TIMEOUT", "30"))  # seconds


# ============================================================================
# TOOL IMPLEMENTATIONS
# ============================================================================

async def query_pest_disease_rag(pest_name: str, crop: str = "General") -> dict:
    """Query Pests and Diseases RAG API from Render"""
    print(f"🌾 Querying Pests/Diseases RAG API: pest={pest_name}, crop={crop}")
    
    try:
        async with httpx.AsyncClient(timeout=RAG_TIMEOUT) as client:
            # Make RAG API call to PESTS_DISEASES_RAG_URL
            # Build the question
            question_text = f"{pest_name} affecting {crop} crops" if crop and crop != "General" else pest_name
            
            print(f"📤 Sending question: {question_text}")
            response = await client.post(
                f"{PESTS_DISEASES_RAG_URL}/query",
                json={
                    "question": question_text,  # RAG API expects "question" not "query"
                    "top_k": 5  # Number of source chunks to retrieve
                }
            )
            print(f"📥 Response status: {response.status_code}")
            
            if response.status_code == 200:
                rag_result = response.json()
                # RAG API returns {"answer": "...", "sources": [...]}
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
                    "source_details": sources,  # Full source details with scores and chunks
                    "message": f"Information retrieved for {pest_name} from Pests & Diseases RAG API"
                }
            else:
                # Log the full error response for debugging
                error_detail = response.text
                print(f"❌ RAG API Error {response.status_code}: {error_detail}")
                return {
                    "status": "error",
                    "pest_name": pest_name,
                    "crop": crop,
                    "message": f"Pests/Diseases RAG API error: {response.status_code}",
                    "error_detail": error_detail[:500],  # Include error details
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
    """Query Government Schemes RAG API from Render"""
    print(f"🏛️  Querying Government Schemes RAG API: scheme={scheme_type}, state={state}")
    
    try:
        async with httpx.AsyncClient(timeout=RAG_TIMEOUT) as client:
            # Build the question
            if state and state != "All India":
                question_text = f"tell me the schemes related to {scheme_type} in {state}"
            else:
                question_text = f"tell me the schemes related to {scheme_type}"
            
            print(f"📤 Sending question: {question_text}")
            response = await client.post(
                f"{GOVT_SCHEMES_RAG_URL}/query",
                json={
                    "question": question_text,  # RAG API expects "question" not "query"
                    "top_k": 5  # Number of source chunks to retrieve
                }
            )
            print(f"📥 Response status: {response.status_code}")
            
            if response.status_code == 200:
                rag_result = response.json()
                # RAG API returns {"answer": "...", "sources": [...]}
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
                    "source_details": sources,  # Full source details with scores and chunks
                    "message": f"Scheme information retrieved for {scheme_type} from Government Schemes RAG API"
                }
            else:
                # Log the full error response for debugging
                error_detail = response.text
                print(f"❌ RAG API Error {response.status_code}: {error_detail}")
                return {
                    "status": "error",
                    "scheme_type": scheme_type,
                    "state": state,
                    "message": f"Government Schemes RAG API error: {response.status_code}",
                    "error_detail": error_detail[:500],  # Include error details
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


@app.get("/")
async def root():
    """Root endpoint - for health checks and info"""
    return {
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


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Agricultural MCP Server"
    }


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
    print("   GET  /              - Root info endpoint")
    print("   GET  /health        - Health check")
    print("   POST /getToolsList  - List available tools")
    print("   POST /callTool      - Execute a tool")
    print("\n" + "=" * 70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8005)