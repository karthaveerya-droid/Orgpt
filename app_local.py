"""
app_local.py
------------
Runs Orgpt locally with chat interface and full backend initialization.
"""

import os
import sys
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

# ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingestion.Swagger_connector.swagger_connector import extract_text_from_swagger_sources
from processing.chunker import chunk_texts
from processing.embedder import Embedder
from vector_store.store import VectorStore
from retrieval.rag_engine import RAGEngine
from llm.llm_layer import LLMHandler

# --------------------------------------------------------------------------------
# ⚙️ Setup FastAPI
# --------------------------------------------------------------------------------
app = FastAPI(title="Orgpt Local Chat")
templates = Jinja2Templates(directory="templates")

docs = extract_text_from_swagger_sources()
chunks = chunk_texts(docs)
embedder = Embedder()
embeddings = embedder.embed(chunks)

vs = VectorStore("swagger")
ids = [f"chunk_{i}" for i in range(len(chunks))]
vs.add(ids=ids, texts=chunks, embeddings=embeddings)
print("Swagger data indexed.")

def query_orgpt(query):
    rag = RAGEngine()
    retrieved = rag.retrieve(query, top_k=3)
    context = "\n".join(retrieved["documents"][0])
    llm = LLMHandler()
    answer = llm.ask(query, context)
    print("Answer:", answer)
    return answer

# --------------------------------------------------------------------------------
# 🌐 Web Routes
# --------------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve chat interface."""
    return templates.TemplateResponse("chat.html", {"request": request})


@app.post("/chat")
async def chat(query: str = Form(...)):
    """Chat endpoint."""
    try:
        print(f" User Query: {query}")

        answer = query_orgpt(query)

        # ✅ make sure answer is printable + serializable
        if not isinstance(answer, str):
            answer = str(answer)

        print(f"Answer: {answer[:200]}...")  # log first part
        return JSONResponse(content={"answer": answer})
        
    except Exception as e:
        print(" Error:", e)
        return JSONResponse({"error": str(e)})


# --------------------------------------------------------------------------------
# 🏁 Entry point
# --------------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
