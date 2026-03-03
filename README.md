# Alumnx MCP Server

A Model Context Protocol (MCP) server for agricultural intelligence, providing tools for pest/disease lookup, government scheme discovery, and SME knowledge retrieval via semantic search.

---

## Features

- **Pests & Diseases** — RAG-powered lookup for crop pest and disease information
- **Government Schemes** — RAG-powered search for agriculture-related government schemes by type and state
- **SME Divesh** — Semantic search over a Pinecone knowledge base (SME-Divesh namespace)
- **MCP + REST** — Dual interface: MCP protocol (via FastMCP) and plain REST (`/callTool`)

---

## Requirements

- Python 3.9+
- Dependencies (install via `pip install -r requirements.txt`):

```
fastmcp
pinecone
sentence-transformers
python-dotenv
uvicorn
httpx
fastapi
```

---

## Environment Variables

Create a `.env` file in the project root with the following variables:

| Variable                | Required | Description                                          |
|-------------------------|----------|------------------------------------------------------|
| `PESTS_DISEASES_RAG_URL`| ✅        | Base URL of the Pests & Diseases RAG service         |
| `GOVT_SCHEMES_RAG_URL`  | ✅        | Base URL of the Government Schemes RAG service       |
| `PINECONE_API_KEY`      | ✅        | API key for Pinecone                                 |
| `PINECONE_INDEX`        | ✅        | Name of the Pinecone index to query                  |
| `RAG_TIMEOUT`           | ❌        | HTTP timeout in seconds for RAG calls (default: `30`)|

**Example `.env`:**
```env
PESTS_DISEASES_RAG_URL= ___URL__
GOVT_SCHEMES_RAG_URL= __URL__
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_INDEX=your-index-name
RAG_TIMEOUT=30
```

---

## Running the Server

```bash
python alumnx_mcp_server.py
```

The server starts on **port 9000** by default.

| Endpoint        | Description                        |
|-----------------|------------------------------------|
| `/mcp`          | MCP protocol endpoint (FastMCP)    |
| `/callTool`     | REST tool call endpoint            |
| `/list-tools`   | Lists all available tools          |
| `/health`       | Health check                       |

---

## MCP Tools

### `pests_and_diseases`
Query the RAG system for information about pests and diseases affecting crops.

| Parameter   | Type   | Required | Default     | Description                          |
|-------------|--------|----------|-------------|--------------------------------------|
| `pest_name` | string | ✅        | —           | Name of the pest or disease          |
| `crop`      | string | ❌        | `"General"` | Crop affected by the pest or disease |

**Example response:**
```json
{
  "status": "success",
  "information": "...",
  "sources": ["..."]
}
```

---

### `govt_schemes`
Query the RAG system for government schemes related to agriculture.

| Parameter     | Type   | Required | Default        | Description                          |
|---------------|--------|----------|----------------|--------------------------------------|
| `scheme_type` | string | ✅        | —              | Type or topic of the scheme          |
| `state`       | string | ❌        | `"All India"`  | State for which to retrieve schemes  |

**Example response:**
```json
{
  "status": "success",
  "information": "...",
  "sources": ["..."]
}
```

---

### `sme_divesh`
Semantic search over the SME-Divesh Pinecone namespace using `all-MiniLM-L6-v2` embeddings.

| Parameter | Type    | Required | Default | Description                        |
|-----------|---------|----------|---------|------------------------------------|
| `query`   | string  | ✅        | —       | The search query                   |
| `top_k`   | integer | ❌        | `5`     | Number of top results to return    |

**Example response:**
```json
{
  "status": "success",
  "query": "crop irrigation techniques",
  "results": [
    {
      "score": 0.91,
      "text": "...",
      "source": "...",
      "chunk_index": 2
    }
  ]
}
```

---

## REST API Usage

All tools are also callable via the `/callTool` POST endpoint:

```bash
curl -X POST http://localhost:9000/callTool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "pests_and_diseases",
    "arguments": {
      "pest_name": "aphids",
      "crop": "wheat"
    }
  }'
```

---

## Architecture

```
┌─────────────────────────────────────────┐
│            Alumnx MCP Server            │
│                                         │
│  FastAPI App                            │
│  ├── /mcp          ← FastMCP (MCP)      │
│  ├── /callTool     ← REST interface     │
│  ├── /list-tools   ← Tool discovery     │
│  └── /health       ← Health check       │
│                                         │
│  Tools                                  │
│  ├── pests_and_diseases → RAG HTTP call │
│  ├── govt_schemes       → RAG HTTP call │
│  └── sme_divesh         → Pinecone      │
└─────────────────────────────────────────┘
```

---

