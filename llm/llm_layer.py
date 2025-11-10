from openai import OpenAI

class LLMHandler:
    def __init__(self, api_key=None):
        self.client = OpenAI(api_key="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")

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
