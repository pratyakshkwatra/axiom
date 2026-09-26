import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

class AxiomAgent:
    def __init__(self):
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)

    def process_chat(self, message: str, context: str = ""):
        system_prompt = (
            "You are AXIOM, the enterprise context and action AI. "
            "You have access to organizational context, such as Freshservice tickets. "
            "Use the provided context to answer the user's questions clearly, concisely, and professionally. "
            "Format your output in clean Markdown."
        )
        
        prompt_with_context = message
        if context:
            prompt_with_context = f"Here is some organizational context retrieved from the systems (e.g. Freshservice):\n{context}\n\nUser Request: {message}"

        response = self.client.messages.create(
            model="claude-5-sonnet-latest",
            max_tokens=1024,
            system=system_prompt,
            messages=[
                {"role": "user", "content": prompt_with_context}
            ]
        )
        
        return response.content[0].text

axiom_agent = AxiomAgent()
