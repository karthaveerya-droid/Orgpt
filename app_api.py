# app_api.py
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

# Serve root page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

# Main query endpoint (POST /query)
@app.post("/query")
async def query(query: str = Form(...)):
    try:
        print(f"\nUser Query: {query}")
        rag = RAGEngine()
        answer = rag.ask(query)
        print(f"Answer: {answer[:400]}...\n")  # truncate for log clarity
        return JSONResponse({"answer": answer})
    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse({"error": str(e)})
    
@app.post("/chat")
async def chat(query: str = Form(...)):
    try:
        print(f"\nUser Query: {query}")
        rag = RAGEngine()
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
