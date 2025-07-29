# llm/backends/llm_backend.py
import os

class GenericProvider:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")

    def query(self, system_prompt, user_prompt, max_tokens=300):
        # Abstract method to be implemented by subclasses for each LLM provider
        raise NotImplementedError("This method should be implemented by subclasses.")