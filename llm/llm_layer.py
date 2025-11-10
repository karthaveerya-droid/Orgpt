from openai import OpenAI

class LLMHandler:
    def __init__(self, api_key=None):
        self.client = OpenAI(api_key="testagain")

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
