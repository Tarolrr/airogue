# llm/providers/openai_provider.py
from openai import OpenAI

# client = OpenAI(api_key=self.api_key)
from providers.generic_provider import GenericProvider

class OpenAIProvider(GenericProvider):
    def query(self, system_prompt, user_prompt, max_tokens=300):
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens
        )
        # Assuming we want the last message in the conversation, which should be the AI's response
        return response.choices[0].message.content.strip()