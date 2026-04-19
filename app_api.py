# app_api.py
"""
OrgGPT FastAPI Server
====================


Endpoints:
- POST /query
- POST /chat
- GET /monitor: ChromaDB monitor interface
- GET /chromadb/status: ChromaDB status API
"""

import os
import sys
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

# Local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from retrieval.rag_engine import RAGEngine

app = FastAPI(title="Orgpt Swagger Agent", version="1.0.0")

# Enable CORS for public chat demos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup templates (chat.html)
templates = Jinja2Templates(directory="templates")

# Collection metadata
COLLECTION_INFO = {
    "unified_knowledge": {
        "name": "Unified Knowledge Base",
        "description": "All sources combined (Swagger + Datadog Catalog + Datadog SLOs)",
        "icon": "�",
        "note": "Unified search across all data sources"
    }
}

# Serve root page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="chat.html"
    )

# Main query endpoint (POST /query) - Compatible with main branch
@app.post("/query")
async def query(query: str = Form(...), collection: str = Form(None)):
    # Always use unified collection
    collection = "unified_knowledge"
    
    try:
        print(f"\n{'='*80}")
        print(f" Query: {query}")
        print(f" Collection: {collection}")
        print(f"{'='*80}")
        
        # Query RAG engine
        rag = RAGEngine(store_name=collection)
        answer = rag.ask(query)
        
        # Get collection info
        col_info = COLLECTION_INFO.get(collection, {
            "name": collection,
            "icon": "📦",
            "note": f"Custom collection: {collection}"
        })
        
        print(f" Answer generated ({len(answer)} chars)")
        print(f"{'='*80}\n")
        
        # Build response with metadata
        response_data = {
            "answer": answer,
            "source": collection,
            "source_name": col_info.get("name", collection),
            "source_icon": col_info.get("icon", "📦"),
            "note": col_info.get("note", "")
        }
        
        return JSONResponse(response_data)
        
    except Exception as e:
        print(f" Error: {e}\n")
        return JSONResponse({
            "error": str(e),
            "source": collection
        }, status_code=500)


@app.post("/chat")
async def chat(query: str = Form(...)):
    """Chat endpoint - alias for /query using unified collection."""
    try:
        print(f"\nUser Query: {query}")
        # Use unified_knowledge collection (same as /query endpoint)
        rag = RAGEngine(store_name="unified_knowledge")
        answer = rag.ask(query)
        return JSONResponse({"answer": answer})
    except Exception as e:
        return JSONResponse({"error": str(e)})

# Health check
@app.get("/health")
async def health():
    return {"status": "ok", "message": "Orgpt Swagger Agent is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

