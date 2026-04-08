"""
app_with_datadog.py
-------------------
Enhanced FastAPI application with Datadog APM integration.

This version adds:
  - Datadog data ingestion endpoints
  - Mixed source retrieval (Swagger + Datadog)
  - Service topology queries
  - Status monitoring
"""

import os
import sys
import logging
from typing import Optional
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Form, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ✅ Ensure local modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from processing.chunker import chunk_texts
from processing.embedder import Embedder
from vector_store.store import VectorStore
from retrieval.rag_engine import RAGEngine

from ingestion.Datadog_connector import DatadogConnector, extract_datadog_data
from ingestion.Datadog_connector.datadog_store_integration import DatadogVectorStoreIntegration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# LIFESPAN EVENT HANDLER (Modern FastAPI approach - Recommended since v0.93.0)
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI application lifespan context manager.
    
    This context manager handles the complete lifecycle of the OrgGPT application,
    using the modern FastAPI pattern (v0.93.0+). It replaces the deprecated
    @app.on_event("startup") and @app.on_event("shutdown") decorators.
    
    Architecture:
    - STARTUP PHASE: Initialize stateful resources (Datadog integration, vector store)
    - RUNNING PHASE: Application serves HTTP requests (marked by 'yield')
    - SHUTDOWN PHASE: Cleanup resources and log graceful shutdown
    
    Key Benefits:
    1. Single unified function (cleaner code structure)
    2. Guaranteed cleanup execution (even on errors)
    3. Future-proof (officially recommended by FastAPI)
    4. Better async/await semantics
    
    Environment Variables:
    - DATADOG_POC_ENABLED: Whether to enable Datadog integration (default: "true")
    - DATADOG_CACHE_TTL: TTL for Datadog cache in seconds (default: "3600")
    - DATADOG_AUTO_INGEST: Auto-ingest Datadog data on startup (default: "false")
    
    Execution Flow:
    ┌─────────────────────────────────────────────────────────────┐
    │ 1. STARTUP: Initialize resources                            │
    │    ├─ Load environment configuration                        │
    │    ├─ Instantiate DatadogVectorStoreIntegration (if enabled)│
    │    └─ Optionally: Ingest Datadog data                      │
    ├─────────────────────────────────────────────────────────────┤
    │ 2. YIELD: Application ready for requests                    │
    │    ├─ Handle HTTP requests                                  │
    │    ├─ Serve chat endpoints                                  │
    │    └─ Manage data retrieval                                 │
    ├─────────────────────────────────────────────────────────────┤
    │ 3. SHUTDOWN: Cleanup on termination                         │
    │    ├─ Log shutdown event                                    │
    │    └─ Release resources                                     │
    └─────────────────────────────────────────────────────────────┘
    
    Args:
        app (FastAPI): The FastAPI application instance
        
    Yields:
        None: Control is yielded to the application for request handling
        
    Raises:
        Exception: Any errors during startup are logged and can prevent app start
    """
    
    # ========================================================================
    # STARTUP PHASE: Initialize application resources
    # ========================================================================
    
    logger.info("🚀 OrgGPT starting up...")
    
    # Initialize Datadog integration if enabled
    if app_state.datadog_enabled:
        logger.info("📊 Datadog integration enabled - initializing...")
        try:
            # Create the Datadog vector store integration with configured TTL
            app_state.datadog_integration = DatadogVectorStoreIntegration(
                vector_store=app_state.vector_store,
                cache_ttl_seconds=int(os.getenv("DATADOG_CACHE_TTL", "3600"))
            )
            logger.debug("✓ DatadogVectorStoreIntegration instance created successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Datadog integration: {e}", exc_info=True)
            raise
        
        # Optional: Auto-ingest Datadog catalog data on application startup
        # This is useful for pre-warming the vector store cache
        if os.getenv("DATADOG_AUTO_INGEST", "false").lower() == "true":
            logger.info("Auto-ingestion enabled - fetching Datadog catalog data...")
            try:
                await ingest_datadog_data()
                logger.info("✓ Datadog data ingestion completed successfully")
            except Exception as e:
                logger.error(f"Failed to auto-ingest Datadog data: {e}", exc_info=True)
                # Note: We don't raise here to allow app startup even if ingestion fails
    else:
        logger.info("⚠️  Datadog integration disabled - app will run in standalone mode")
    
    logger.info("✅ OrgGPT ready to serve requests")
    
    # ========================================================================
    # YIELD: Application enters running state
    # ========================================================================
    # The 'yield' statement marks the transition point:
    # - Before yield: Startup code (runs once when app starts)
    # - After yield: Shutdown code (runs once when app terminates)
    # - Between startup and shutdown: Application handles requests
    
    yield
    
    # ========================================================================
    # SHUTDOWN PHASE: Cleanup and graceful termination
    # ========================================================================
    
    logger.info("Shutting down OrgGPT...")
    
    # Cleanup Datadog integration if it was initialized
    if app_state.datadog_integration is not None:
        try:
            logger.debug("Cleaning up Datadog integration resources...")
            # Future: Add explicit cleanup methods if needed
            app_state.datadog_integration = None
            logger.debug("✓ Datadog integration cleaned up")
        except Exception as e:
            logger.error(f"Error during Datadog cleanup: {e}", exc_info=True)
    
    logger.info("✅ OrgGPT shutdown complete")


# Initialize FastAPI app
app = FastAPI(
    title="OrgGPT - Enhanced with Datadog APM",
    version="1.0.0-datadog-poc",
    lifespan=lifespan
)

# Initialize templates
templates = Jinja2Templates(directory="templates")

# Global state
class AppState:
    def __init__(self):
        self.vector_store = VectorStore(collection_name="datadog_catalog")  # ✨ Updated to use Catalog Entity collection
        self.embedder = Embedder()
        self.rag_engine = RAGEngine(store_name="datadog_catalog")
        self.datadog_integration: Optional[DatadogVectorStoreIntegration] = None
        self.last_datadog_sync: Optional[datetime] = None
        self.datadog_enabled = os.getenv("DATADOG_POC_ENABLED", "true").lower() == "true"

app_state = AppState()


# ============================================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """System health check."""
    return {
        "status": "healthy",
        "datadog_enabled": app_state.datadog_enabled,
        "last_datadog_sync": app_state.last_datadog_sync.isoformat() 
            if app_state.last_datadog_sync else None,
    }


@app.get("/status")
async def status():
    """Get detailed system and Datadog integration status."""
    status_info = {
        "system": {
            "timestamp": datetime.now().isoformat(),
            "datadog_enabled": app_state.datadog_enabled,
        }
    }
    
    if app_state.datadog_integration:
        status_info["datadog"] = app_state.datadog_integration.get_ingestion_status()
    
    return status_info


# ============================================================================
# DATADOG INTEGRATION ENDPOINTS
# ============================================================================

@app.post("/api/datadog/ingest")
async def ingest_datadog_data():
    """
    Manually trigger Datadog APM data ingestion.
    
    This endpoint:
      1. Extracts service catalog, dependencies, SLOs, and ownership from Datadog
      2. Transforms to text documents
      3. Embeds and stores in vector database
    
    Returns ingestion metadata and statistics.
    """
    try:
        if not app_state.datadog_enabled:
            return JSONResponse(
                {"error": "Datadog integration is not enabled"},
                status_code=400
            )
        
        logger.info("Triggering Datadog data ingestion...")
        
        # Initialize integration if needed
        if app_state.datadog_integration is None:
            app_state.datadog_integration = DatadogVectorStoreIntegration(
                vector_store=app_state.vector_store,
                cache_ttl_seconds=int(os.getenv("DATADOG_CACHE_TTL", "3600"))
            )
        
        # Ingest data
        result = app_state.datadog_integration.ingest_datadog_data()
        app_state.last_datadog_sync = datetime.now()
        
        return JSONResponse(result)
    
    except Exception as e:
        logger.error(f"Error during Datadog ingestion: {e}", exc_info=True)
        return JSONResponse(
            {"error": str(e), "status": "failed"},
            status_code=500
        )


@app.get("/api/datadog/status")
async def get_datadog_status():
    """Get Datadog integration status and metadata."""
    if app_state.datadog_integration is None:
        return {"status": "not_initialized"}
    
    return app_state.datadog_integration.get_ingestion_status()


@app.get("/api/datadog/services")
async def list_datadog_services():
    """
    Get list of services from Datadog Catalog Entity API.
    
    Returns all services with basic metadata (name, owner, team).
    Uses modern /api/v2/catalog/entity endpoint.
    """
    try:
        connector = DatadogConnector()
        # ✨ Use Catalog Entity API (modern)
        entities = connector.extract_catalog_entities(kinds=["service"])
        
        # Transform to simple format
        service_list = [
            {
                "name": e.get("attributes", {}).get("name"),
                "displayName": e.get("attributes", {}).get("displayName"),
                "owner": e.get("attributes", {}).get("owner"),
                "team": e.get("attributes", {}).get("team"),
                "description": e.get("attributes", {}).get("description", ""),
            }
            for e in entities
        ]
        
        logger.info(f"✓ Retrieved {len(service_list)} services from Catalog Entity")
        return {"count": len(service_list), "services": service_list}
    
    except Exception as e:
        logger.error(f"Error fetching services: {e}")
        return JSONResponse(
            {"error": str(e)},
            status_code=500
        )


@app.get("/api/datadog/service/{service_name}")
async def get_service_details(service_name: str):
    """
    Get detailed information about a specific service.
    
    Args:
        service_name: Name of the service (e.g., "payment-api")
    
    Returns:
        Detailed service profile with metadata, relationships, and schema info.
        Uses modern /api/v2/catalog/entity endpoint.
    """
    try:
        connector = DatadogConnector()
        
        # ✨ Use Catalog Entity API to find service by reference
        # Query by official Catalog Entity format: "service:name"
        entity = connector.catalog_extractor.extract_entity_by_ref(
            f"service:{service_name}"
        )
        
        if not entity:
            logger.warning(f"Service not found: {service_name}")
            return JSONResponse(
                {"error": f"Service not found: {service_name}"},
                status_code=404
            )
        
        # ✨ Transform to markdown document using Catalog Entity transformer
        profile_doc = connector.catalog_transformer.transform_entity_with_schema(entity)
        
        logger.info(f"✓ Retrieved service details: {service_name}")
        return {
            "service": service_name,
            "profile": profile_doc,
            "metadata": {
                "owner": entity.get("attributes", {}).get("owner"),
                "team": entity.get("attributes", {}).get("team"),
                "kind": entity.get("attributes", {}).get("kind"),
            }
        }
    
    except Exception as e:
        logger.error(f"Error fetching service details: {e}")
        return JSONResponse(
            {"error": str(e)},
            status_code=500
        )


# ============================================================================
# ENHANCED CHAT ENDPOINTS
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve main chat interface."""
    return templates.TemplateResponse("chat.html", {"request": request})


@app.post("/chat")
async def chat(query: str = Form(...), include_datadog: bool = Query(True)):
    """
    Enhanced chat endpoint that can use both Swagger and Datadog data.
    
    Query parameters:
      - query: The user's question
      - include_datadog: Whether to include Datadog data in retrieval (default: true)
    """
    try:
        logger.info(f"Processing query: {query}")
        
        # For now, use existing RAG engine
        # In production, you'd route queries to specialized retrievers
        answer = app_state.rag_engine.ask(query)
        
        return JSONResponse({"answer": answer})
    
    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        return JSONResponse(
            {"error": str(e)},
            status_code=500
        )


@app.post("/chat/datadog-specific")
async def chat_datadog_specific(query: str = Form(...)):
    """
    Chat endpoint specifically for Datadog-related queries.
    
    Example queries:
      - "What services depend on the payment service?"
      - "Which teams own the auth service?"
      - "What's the SLO for our API gateway?"
    """
    try:
        logger.info(f"Processing Datadog query: {query}")
        
        # Use RAG engine to retrieve Datadog-specific context
        answer = app_state.rag_engine.ask(query)
        
        return JSONResponse({
            "answer": answer,
            "query_type": "datadog_topology"
        })
    
    except Exception as e:
        logger.error(f"Error processing Datadog query: {e}")
        return JSONResponse(
            {"error": str(e)},
            status_code=500
        )




# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
