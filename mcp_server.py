#!/usr/bin/env python3
"""
Agricultural MCP Server

"""

import json
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import httpx
import os
from fastmcp import FastMCP

# ============================================================================
# RAG API CONFIGURATION
# ============================================================================

PESTS_DISEASES_RAG_URL = os.getenv(
    "PESTS_DISEASES_RAG_URL",
    "https://agrigpt-backend-rag-pest-and-disease.onrender.com"
)

GOVT_SCHEMES_RAG_URL = os.getenv(
    "GOVT_SCHEMES_RAG_URL",
    "https://agrigpt-backend-rag-government-schemes-1.onrender.com"
)

RAG_TIMEOUT = int(os.getenv("RAG_TIMEOUT", "30"))

# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(title="Agricultural MCP Server")

# ============================================================================
# MCP INITIALIZATION
# ============================================================================

mcp = FastMCP(
    name="Agricultural Tools MCP Server",
    description="Provides agricultural pest/disease and government scheme information"
)

# Mount MCP endpoint
app.mount("/mcp", mcp.app)

# ============================================================================
# TOOL IMPLEMENTATIONS (UNCHANGED LOGIC)
# ============================================================================

async def query_pest_disease_rag(pest_name: str, crop: str = "General") -> dict:

    try:
        async with httpx.AsyncClient(timeout=RAG_TIMEOUT) as client:

            question_text = (
                f"{pest_name} affecting {crop} crops"
                if crop and crop != "General"
                else pest_name
            )

            response = await client.post(
                f"{PESTS_DISEASES_RAG_URL}/query",
                json={
                    "question": question_text,
                    "top_k": 5
                }
            )

            if response.status_code == 200:

                rag_result = response.json()

                return {
                    "status": "success",
                    "pest_name": pest_name,
                    "crop": crop,
                    "information": rag_result.get("answer"),
                    "sources": rag_result.get("sources", [])
                }

            return {"status": "error"}

    except Exception as e:
        return {"status": "error", "message": str(e)}


async def query_govt_scheme_rag(scheme_type: str, state: str = "All India") -> dict:

    try:
        async with httpx.AsyncClient(timeout=RAG_TIMEOUT) as client:

            question_text = (
                f"tell me the schemes related to {scheme_type} in {state}"
                if state != "All India"
                else f"tell me the schemes related to {scheme_type}"
            )

            response = await client.post(
                f"{GOVT_SCHEMES_RAG_URL}/query",
                json={
                    "question": question_text,
                    "top_k": 5
                }
            )

            if response.status_code == 200:

                rag_result = response.json()

                return {
                    "status": "success",
                    "scheme_type": scheme_type,
                    "state": state,
                    "information": rag_result.get("answer"),
                    "sources": rag_result.get("sources", [])
                }

            return {"status": "error"}

    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================================
# MCP TOOL REGISTRATION (NEW)
# ============================================================================

@mcp.tool()
async def pests_and_diseases(
    pest_name: str,
    crop: str = "General"
) -> dict:
    """
    Query agricultural pests and diseases knowledge base
    """
    return await query_pest_disease_rag(pest_name, crop)


@mcp.tool()
async def govt_schemes(
    scheme_type: str,
    state: str = "All India"
) -> dict:
    """
    Query agricultural government schemes knowledge base
    """
    return await query_govt_scheme_rag(scheme_type, state)


# ============================================================================
# EXISTING ENDPOINTS (UNCHANGED)
# ============================================================================

class ToolCallRequest(BaseModel):
    name: str
    arguments: Dict[str, Any]


@app.get("/")
async def root():
    return {
        "status": "healthy",
        "service": "Agricultural MCP Server",
        "mcp_endpoint": "/mcp"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/getToolsList")
async def list_tools():

    return {
        "tools": [
            {
                "name": "pests_and_diseases",
                "description": "Query pest and disease information"
            },
            {
                "name": "govt_schemes",
                "description": "Query government schemes"
            }
        ]
    }


@app.post("/callTool")
async def call_tool(request: ToolCallRequest):

    if request.name == "pests_and_diseases":

        result = await query_pest_disease_rag(
            request.arguments.get("pest_name"),
            request.arguments.get("crop", "General")
        )

        return {"result": result}

    elif request.name == "govt_schemes":

        result = await query_govt_scheme_rag(
            request.arguments.get("scheme_type"),
            request.arguments.get("state", "All India")
        )

        return {"result": result}

    raise HTTPException(404, "Unknown tool")


# ============================================================================
# SERVER START
# ============================================================================

if __name__ == "__main__":

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8005
    )
