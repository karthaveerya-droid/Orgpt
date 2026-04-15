"""
Embedder module for Orgpt
-------------------------
Creates vector embeddings from text using the best available backend.
Works without torch and supports CPU-only environments (Python 3.13 safe).
"""

import logging
import numpy as np

logger = logging.getLogger(__name__)

class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: str = "cpu"):
        """
        Initialize the embedder. Attempts backends in this order:
        1. sentence-transformers (preferred)
        2. transformers (fallback)
        3. random numpy vectors (last resort placeholder)
        """
        self.model_name = model_name
        self.device = device
        self.backend = None
        self.model = None

        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name, device=device)
            self.backend = "sentence-transformers"
            logger.info(f"Using SentenceTransformer backend: {model_name}")
        except Exception as e:
            logger.warning(f"SentenceTransformer backend unavailable: {e}")
            try:
                from transformers import AutoTokenizer, AutoModel
                import torch

                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModel.from_pretrained(model_name)
                self.backend = "transformers"
                self.torch = torch
                logger.info(f"Using Transformers fallback backend: {model_name}")
            except Exception as e2:
                logger.error(f"No embedding backend available ({e2}). Falling back to random.")
                self.backend = "none"

    def embed(self, texts):
        """
        Generate embeddings for a list of texts.
        Returns a list of numpy arrays.
        """
        if isinstance(texts, str):
            texts = [texts]

        # --- sentence-transformers backend ---
        if self.backend == "sentence-transformers":
            return self.model.encode(texts, convert_to_numpy=True)

        # --- transformers fallback ---
        elif self.backend == "transformers":
            self.model.eval()
            embeddings = []
            with self.torch.no_grad():
                for text in texts:
                    inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
                    outputs = self.model(**inputs)
                    # Average pooling of last hidden state
                    last_hidden = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
                    embeddings.append(last_hidden)
            return np.array(embeddings)

        # --- no backend: dummy random vectors ---
        else:
            logger.warning("Returning random embeddings (no model available).")
            return np.random.rand(len(texts), 384)
