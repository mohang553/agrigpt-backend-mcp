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

# RAG API for Government Schemes (Placeholder - set when available)
GOVT_SCHEMES_RAG_URL = os.getenv(
    "GOVT_SCHEMES_RAG_URL",
    "http://localhost:8002"
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
            response = await client.post(
                f"{PESTS_DISEASES_RAG_URL}/query",
                json={
                    "query": f"Tell me about {pest_name} pest/disease affecting {crop} crops. Include identification, symptoms, and management strategies."
                }
            )
            
            if response.status_code == 200:
                rag_result = response.json()
                return {
                    "status": "success",
                    "pest_name": pest_name,
                    "crop": crop,
                    "information": rag_result.get("result", rag_result.get("answer", "No information found")),
                    "sources": rag_result.get("sources", []),
                    "message": f"Information retrieved for {pest_name} from Pests & Diseases RAG API"
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
    """Query Government Schemes knowledge base - Currently using mock responses"""
    print(f"🏛️  Querying Government Schemes knowledge base: scheme={scheme_type}, state={state}")
    
    # Mock sample responses for different schemes
    mock_responses = {
        "crop insurance": {
            "answer": f"Crop Insurance Schemes in {state}: These schemes provide financial protection to farmers against crop losses due to natural calamities. Benefits: Coverage up to 70-80% of the crop value, premium subsidy of 50% for small/marginal farmers. Eligibility Criteria: Active farmers with valid land ownership documents, ability to pay premium share. Required Documents: Land ownership certificate, ID proof, bank account details. Processing Time: 15-30 days from application. Major schemes include Pradhan Mantri Fasal Bima Yojana (PMFBY) and Restructured Weather-based Crop Insurance Scheme (RWBCIS). Premium rates vary by crop and location.",
            "sources": ["agriculture_ministry_schemes.pdf", "crop_insurance_guidelines.txt"]
        },
        "subsidy": {
            "answer": f"Agricultural Subsidies in {state}: Various subsidy programs available for farmers to enhance agricultural productivity. Benefits: Direct payment of 30-50% of equipment cost, input subsidies for seeds, fertilizers, and pesticides. Eligibility Criteria: Landholding limit of 2-4 hectares (varies by scheme), must be primary occupation farmer. Required Documents: Aadhar card, land records, bank details, agricultural proof. Processing Time: 30-45 days. Subsidies cover agricultural equipment, solar pumps, drip irrigation systems, and improved crop varieties.",
            "sources": ["subsidies_handbook.pdf", "government_schemes_2024.txt"]
        },
        "farmer loan": {
            "answer": f"Farmer Loans in {state}: Institutional credit facilities for agricultural and allied activities. Benefits: Loan amount up to 5 lakh rupees at concessional rate of 4-7% per annum, agricultural debt waiver eligibility. Eligibility Criteria: Farmer with valid identification and land records, age 18-65 years. Required Documents: Land ownership proof, identity proof, income certificate, bank statements. Processing Time: 7-15 days for disbursement. Credit available for crop production, equipment purchase, land development, and allied activities like dairy farming.",
            "sources": ["financial_assistance_guide.pdf", "bank_schemes_2024.txt"]
        }
    }
    
    # Return mock response based on scheme type, default to a generic response
    scheme_key = scheme_type.lower().strip()
    if scheme_key in mock_responses:
        response = mock_responses[scheme_key]
    else:
        # Generic response for unknown schemes
        response = {
            "answer": f"Agricultural Schemes for {scheme_type} in {state}: This category of schemes is designed to provide financial assistance and support to farmers. To get specific information about {scheme_type} schemes available in your state, please contact your local agricultural office or the State Agricultural Department. General requirements typically include valid identification, land records, and bank account details. Processing times vary based on scheme complexity and documentation requirements.",
            "sources": ["general_schemes_database.txt"]
        }
    
    return {
        "status": "success",
        "scheme_type": scheme_type,
        "state": state,
        "information": response.get("answer", "No information found"),
        "sources": response.get("sources", []),
        "message": f"Scheme information retrieved for {scheme_type} from Government Schemes knowledge base (Mock Response)"
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