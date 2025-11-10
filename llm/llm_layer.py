from openai import OpenAI
from dotenv import load_dotenv

import os

# Load variables from .env
load_dotenv()

# Access them like this:
openai_api_key = os.getenv("OPENAI_API_KEY")

class LLMHandler:
    def __init__(self, api_key=None):
        self.client = OpenAI(api_key=openai_api_key)

    def ask(self, query, context):
        prompt = f"Context:\n{context}\n\nQuestion:\n{query}\nAnswer:"
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    def generate(self, prompt):
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
