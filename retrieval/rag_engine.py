from sentence_transformers import SentenceTransformer
from sentence_transformers import SentenceTransformer
from vector_store.store import VectorStore
from llm.llm_layer import LLMHandler  # assuming you have this component

class RAGEngine:
    def __init__(self, store_name="swagger"):
        """
        Initialize the RAG engine with an embedder and a vector store.
        """
        print(" Initializing RAG Engine...")
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.vs = VectorStore(store_name)
        self.llm = LLMHandler()  # use your existing LLM wrapper
        print(" RAG Engine initialized.")

    def retrieve(self, query, top_k=3):
        """
        Retrieve top-k relevant chunks based on the query.
        """
        q_embed = self.embedder.encode([query])[0]
        return self.vs.search(q_embed, top_k)

    def ask(self, query, top_k=5):
        print(f" Processing query: {query}")
        retrieved = self.retrieve(query, top_k=top_k)

        if not retrieved:
            return "No relevant context found in the current knowledge base."
        
        print("Retrieved embedded index")

        context = "\n".join(retrieved["documents"][0])

        prompt = (
            f"Use the following API documentation context to answer:\n\n"
            f"{context}\n\n"
            f"Question: {query}\n\n"
            f"Answer clearly and include any request/response examples if available."
        )

        answer = self.llm.generate(prompt)
        print("Answer:", answer)

        # This line is essential
        return answer
