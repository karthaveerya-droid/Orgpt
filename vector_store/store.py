import chromadb
import os

class VectorStore:
    def __init__(self, collection_name="swagger", reset=False):
        """
        Initialize Vector Store with automatic Docker/Local detection.
        
        Args:
            collection_name: Name of the ChromaDB collection
            reset: If True, delete and recreate the collection (useful for rebuilding index)
        
        Uses environment variable CHROMA_CLIENT_TYPE to determine client:
        - "http" or "docker": Use HttpClient for Docker ChromaDB
        - "persistent" or unset: Use PersistentClient for local storage
        """
        client_type = os.getenv("CHROMA_CLIENT_TYPE", "persistent").lower()
        
        if client_type in ["http", "docker"]:
            # Docker HTTP client
            host = os.getenv("CHROMA_HOST", "localhost")
            port = int(os.getenv("CHROMA_PORT", "8000"))
            print(f"Connecting to ChromaDB Docker at {host}:{port}")
            self.client = chromadb.HttpClient(host=host, port=port)
        else:
            # Local persistent client
            db_path = os.path.join(os.path.dirname(__file__), "..", "chroma_db")
            print(f" Using local ChromaDB at {db_path}")
            self.client = chromadb.PersistentClient(path=db_path)
        
        # Reset collection if requested (for index rebuilding)
        if reset:
            try:
                self.client.delete_collection(collection_name)
                print(f"✓ Deleted old collection '{collection_name}'")
            except Exception:
                pass  # Collection didn't exist
        
        self.collection = self.client.get_or_create_collection(collection_name)
        print(f"Collection '{collection_name}' ready ({self.collection.count()} docs)")

    def add(self, ids, texts, embeddings, metadata=None):
        self.collection.add(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadata)

    def search(self, query_embedding, top_k=3):
        results = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)
        return results
