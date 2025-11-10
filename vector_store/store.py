import chromadb

class VectorStore:
    def __init__(self, collection_name="swagger"):
        client = chromadb.Client()
        self.collection = client.get_or_create_collection(collection_name)

    def add(self, ids, texts, embeddings, metadata=None):
        self.collection.add(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadata)

    def search(self, query_embedding, top_k=3):
        results = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)
        return results
