#!/usr/bin/env python3
"""
Alumnx MCP Server

"""

import os
import uvicorn
import httpx
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastmcp import FastMCP
import uvicorn
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer


# ============================================================================
# LOAD ENV
# ============================================================================

load_dotenv()

PESTS_DISEASES_RAG_URL = os.getenv("PESTS_DISEASES_RAG_URL")
GOVT_SCHEMES_RAG_URL = os.getenv("GOVT_SCHEMES_RAG_URL")
RAG_TIMEOUT = int(os.getenv("RAG_TIMEOUT", "30"))

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")

# Validate required environment variables
required_vars = {
    "PESTS_DISEASES_RAG_URL": PESTS_DISEASES_RAG_URL,
    "GOVT_SCHEMES_RAG_URL": GOVT_SCHEMES_RAG_URL,
    "PINECONE_API_KEY": PINECONE_API_KEY,
    "PINECONE_INDEX": PINECONE_INDEX,
}

missing = [key for key, value in required_vars.items() if not value]
if missing:
    raise RuntimeError(f"Missing required environment variables: {missing}")


# ============================================================================
# INITIALIZE SERVICES
# ============================================================================

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX)

embed_model = SentenceTransformer("all-MiniLM-L6-v2")

mcp = FastMCP(name="Alumnx Tools MCP Server")

app = FastAPI(title="Alumnx MCP Server")

app.mount("/mcp", mcp.http_app(stateless_http=True))


# ============================================================================
# TOOL IMPLEMENTATIONS
# ============================================================================

async def query_pest_disease_rag(pest_name: str, crop: str = "General") -> dict:
    try:
        async with httpx.AsyncClient(timeout=RAG_TIMEOUT) as client:
            question_text = (
                f"{pest_name} affecting {crop} crops"
                if crop != "General"
                else pest_name
            )

            response = await client.post(
                f"{PESTS_DISEASES_RAG_URL}/query",
                json={"question": question_text, "top_k": 5}
            )

            response.raise_for_status()
            rag_result = response.json()

            return {
                "status": "success",
                "information": rag_result.get("answer"),
                "sources": rag_result.get("sources", [])
            }

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
                json={"question": question_text, "top_k": 5}
            )

            response.raise_for_status()
            rag_result = response.json()

            return {
                "status": "success",
                "information": rag_result.get("answer"),
                "sources": rag_result.get("sources", [])
            }

    except Exception as e:
        return {"status": "error", "message": str(e)}


async def query_sme_divesh(query: str, top_k: int = 5) -> dict:
    try:
        query_embedding = embed_model.encode(query).tolist()

        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            namespace="sme-Divesh"
        )

        matches = [
            {
                "score": m["score"],
                "text": m["metadata"].get("text"),
                "source": m["metadata"].get("source"),
                "chunk_index": m["metadata"].get("chunk_index"),
            }
            for m in results["matches"]
        ]

        return {
            "status": "success",
            "query": query,
            "results": matches
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================================
# MCP TOOL REGISTRATION
# ============================================================================

@mcp.tool()
async def pests_and_diseases(pest_name: str, crop: str = "General") -> dict:
    return await query_pest_disease_rag(pest_name, crop)


@mcp.tool()
async def govt_schemes(scheme_type: str, state: str = "All India") -> dict:
    return await query_govt_scheme_rag(scheme_type, state)


@mcp.tool()
async def sme_divesh(query: str, top_k: int = 5) -> dict:
    return await query_sme_divesh(query, top_k)


# ============================================================================
# REST TOOL CALL SUPPORT
# ============================================================================

class ToolCallRequest(BaseModel):
    name: str
    arguments: Dict[str, Any]


@app.post("/callTool")
async def call_tool(request: ToolCallRequest):

    if request.name == "pests_and_diseases":
        return {"result": await query_pest_disease_rag(
            request.arguments.get("pest_name"),
            request.arguments.get("crop", "General")
        )}

    if request.name == "govt_schemes":
        return {"result": await query_govt_scheme_rag(
            request.arguments.get("scheme_type"),
            request.arguments.get("state", "All India")
        )}

    if request.name == "sme_divesh":
        return {"result": await query_sme_divesh(
            request.arguments.get("query"),
            request.arguments.get("top_k", 5)
        )}

    raise HTTPException(status_code=404, detail="Unknown tool")


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/list-tools")
async def list_tools():
    return {
        "server": "Alumnx Tools MCP Server",
        "tools": [
            {
                "name": "pests_and_diseases",
                "description": "Query the RAG system for information about pests and diseases affecting crops.",
                "parameters": {
                    "pest_name": {"type": "string", "required": True, "description": "Name of the pest or disease to look up."},
                    "crop": {"type": "string", "required": False, "default": "General", "description": "Crop affected by the pest or disease."}
                }
            },
            {
                "name": "govt_schemes",
                "description": "Query the RAG system for information about government schemes related to agriculture.",
                "parameters": {
                    "scheme_type": {"type": "string", "required": True, "description": "Type or topic of the government scheme."},
                    "state": {"type": "string", "required": False, "default": "All India", "description": "State for which to retrieve schemes."}
                }
            },
            {
                "name": "sme_divesh",
                "description": "Retrieve relevant knowledge chunks from the SME-Divesh namespace in Pinecone via semantic search.",
                "parameters": {
                    "query": {"type": "string", "required": True, "description": "The search query."},
                    "top_k": {"type": "integer", "required": False, "default": 5, "description": "Number of top results to return."}
                }
            }
        ]
    }


# ============================================================================
# SERVER START
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)