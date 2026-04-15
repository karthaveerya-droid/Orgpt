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
    return templates.TemplateResponse(
        request=request, 
        name="chat.html"
    )

# Main query endpoint (POST /query)
@app.post("/query")
async def query(query: str = Form(...), collection: str = Form("swagger")):
    try:
        print(f"\nUser Query: {query}")
        print(f"Collection: {collection}")
        rag = RAGEngine(store_name=collection)
        answer = rag.ask(query)
        print(f"Answer: {answer[:400]}...\n")  # truncate for log clarity
        
        # Add metadata based on collection
        response_data = {"answer": answer, "source": collection}
        if collection in ["datadog_poc", "datadog_catalog"]:
            response_data["note"] = "Data from Datadog Catalog (POC mode - sample JSON)"
        elif collection == "datadog_catalog_live":
            response_data["note"] = "Data from Datadog Catalog API (live data)"
        elif collection in ["datadog_slo", "datadog_slo_poc"]:
            response_data["note"] = "Data from Datadog SLO"
        
        return JSONResponse(response_data)
    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse({"error": str(e)})
    
@app.post("/chat")
async def chat(query: str = Form(...), collection: str = Form("swagger")):
    try:
        print(f"\nUser Query: {query}")
        print(f"Collection: {collection}")
        rag = RAGEngine(store_name=collection)
        answer = rag.ask(query)
        
        # Add metadata based on collection
        response_data = {"answer": answer, "source": collection}
        if collection in ["datadog_poc", "datadog_catalog"]:
            response_data["note"] = "Data from Datadog Catalog (POC mode - sample JSON)"
        elif collection == "datadog_catalog_live":
            response_data["note"] = "Data from Datadog Catalog API (live data)"
        elif collection in ["datadog_slo", "datadog_slo_poc"]:
            response_data["note"] = "Data from Datadog SLO"
        
        return JSONResponse(response_data)
    except Exception as e:
        return JSONResponse({"error": str(e)})

# POC Datadog query endpoint
@app.post("/query/datadog-poc")
async def query_datadog_poc(query: str = Form(...)):
    """
    Query the Datadog POC index (built from sample JSON, no API keys).
    Perfect for demonstrations!
    """
    try:
        print(f"\nPOC Query: {query}")
        rag = RAGEngine(store_name="datadog_poc")
        answer = rag.ask(query)
        return JSONResponse({
            "answer": answer,
            "source": "datadog_poc",
            "note": "Data from sample JSON (POC mode)"
        })
    except Exception as e:
        return JSONResponse({"error": str(e), "source": "datadog_poc"})

# Health check
@app.get("/health")
async def health():
    return {"status": "ok", "message": "Orgpt Swagger Agent is running."}

# ChromaDB Monitor Page
@app.get("/monitor", response_class=HTMLResponse)
async def chromadb_monitor(request: Request):
    """ChromaDB connection monitor interface"""
    return templates.TemplateResponse(
        request=request,
        name="chromadb_monitor.html"
    )

# ChromaDB Status API
@app.get("/chromadb/status")
async def chromadb_status():
    """Get ChromaDB connection status and collections info"""
    import chromadb
    import subprocess
    
    status = {
        "docker": {
            "running": False,
            "health": None
        },
        "connection": {
            "success": False,
            "type": None,
            "heartbeat": None
        },
        "collections": [],
        "total_documents": 0
    }
    
    # Check Docker status
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=orgpt-chromadb", "--format", "{{.Status}}"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            status["docker"]["running"] = True
            docker_status = result.stdout.strip()
            
            if "healthy" in docker_status.lower():
                status["docker"]["health"] = "Healthy"
            elif "unhealthy" in docker_status.lower():
                status["docker"]["health"] = "Unhealthy (may still work)"
            else:
                status["docker"]["health"] = "Starting"
    except:
        pass
    
    # Try HTTP connection first
    try:
        host = os.getenv("CHROMA_HOST", "localhost")
        port = int(os.getenv("CHROMA_PORT", "8000"))
        
        client = chromadb.HttpClient(host=host, port=port)
        heartbeat = client.heartbeat()
        
        status["connection"]["success"] = True
        status["connection"]["type"] = f"HTTP ({host}:{port})"
        status["connection"]["heartbeat"] = str(heartbeat)
        
        # Get collections
        collections = client.list_collections()
        for col in collections:
            count = col.count()
            status["collections"].append({
                "name": col.name,
                "count": count
            })
            status["total_documents"] += count
            
    except:
        # Try local persistent client
        try:
            db_path = os.path.join(os.path.dirname(__file__), "chroma_db")
            client = chromadb.PersistentClient(path=db_path)
            
            status["connection"]["success"] = True
            status["connection"]["type"] = f"Persistent ({db_path})"
            status["connection"]["heartbeat"] = "N/A (local)"
            
            # Get collections
            collections = client.list_collections()
            for col in collections:
                count = col.count()
                status["collections"].append({
                    "name": col.name,
                    "count": count
                })
                status["total_documents"] += count
        except:
            pass
    
    return JSONResponse(status)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

