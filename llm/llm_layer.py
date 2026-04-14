from groq import Groq
from dotenv import load_dotenv

import os

# Load variables from .env
load_dotenv()

# Access them like this:
openai_api_key = os.getenv("OPENAI_API_KEY")

class LLMHandler:
    def __init__(self, api_key=None):
        self.client = Groq(api_key=openai_api_key)
        self.model = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

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
