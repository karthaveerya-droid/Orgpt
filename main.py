from ingestion.Swagger_connector.swagger_connector import extract_text_from_swagger_sources
from processing.chunker import chunk_texts
from processing.embedder import Embedder
from vector_store.store import VectorStore
from retrieval.rag_engine import RAGEngine
from llm.llm_layer import LLMHandler

def build_index(swagger_path):
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

if __name__ == "__main__":
    build_index("sample_swagger.json")
    query_orgpt("How do I create a user?")
