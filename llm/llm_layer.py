from groq import Groq
from dotenv import load_dotenv

import os

# Load variables from .env
load_dotenv()

# Access them like this:
openai_api_key = os.getenv("OPENAI_API_KEY")

class LLMHandler:
    def __init__(self, api_key=None, model=None):
        """
        Initialize LLM Handler.
        
        Args:
            api_key: Optional API key override (uses OPENAI_API_KEY env var by default)
            model: Optional model override (uses LLM_MODEL env var by default)
        """
        self.client = Groq(api_key=api_key or openai_api_key)
        self.model = model or os.getenv("LLM_MODEL")
        
        if not self.model:
            raise ValueError(
                "LLM_MODEL must be set in environment variables. "
                "Add LLM_MODEL=your-model-name to your .env file"
            )

    def ask(self, query, context):
        prompt = f"Context:\n{context}\n\nQuestion:\n{query}\nAnswer:"
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    def generate(self, prompt):
        """
        Generate text from a prompt.
        
        Args:
            prompt: The prompt to generate from
            
        Returns:
            Generated text string
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
