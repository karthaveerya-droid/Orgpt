# index_builder.py
import os
import sys

# Ensure imports work when run from root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingestion.Swagger_connector.swagger_connector import extract_text_from_swagger_sources
from ingestion.Document_connector.document_connector import extract_text_from_docs

from processing.chunker import chunk_texts
from processing.embedder import Embedder
from vector_store.store import VectorStore

def build_swagger_index():
    print("\nStarting Swagger data indexing...\n")

    # Step 1: Extract docs from multiple Swagger sources
    docs = extract_text_from_swagger_sources() + extract_text_from_docs()
    print(f"Extracted {len(docs)}  documents.")

    # Step 2: Chunk the text
    chunks = chunk_texts(docs)
    print(f"Chunked into {len(chunks)} text segments.")

    # Step 3: Create embeddings
    embedder = Embedder()
    embeddings = embedder.embed(chunks)
    print(f"Created {len(embeddings)} embeddings.")

    # Step 4: Store in VectorStore
    vs = VectorStore("swagger")
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    vs.add(ids=ids, texts=chunks, embeddings=embeddings)

    print("\nSwagger index build complete and ready for use!\n")

if __name__ == "__main__":
    build_swagger_index()
