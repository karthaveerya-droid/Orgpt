"""
app.py
------
FastAPI-based chat interface for Orgpt.
"""

import os
import sys
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

# ✅ ensure local modules can be imported when using uvicorn
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ✅ imports based on your actual folder structure
from ingestion.swagger_connector import extract_text_from_swagger_sources
from processing.chunker import chunk_texts
from processing.embedder import Embedder
from vector_store.store import VectorStore
from retrieval.rag_engine import RAGEngine  # RAGEngine is in /retrieval/rag_engine.py


app = FastAPI(title="Orgpt Chat Interface")

templates = Jinja2Templates(directory="templates")

# Serve root page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

# Chat endpoint
@app.post("/chat")
async def chat(query: str = Form(...)):
    try:
        answer = RAGEngine().ask(query)
        return JSONResponse({"answer": answer})
    except Exception as e:
        return JSONResponse({"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
