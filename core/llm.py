import os
from openai import AsyncOpenAI
from typing import List, Dict, Any

class LLMClient:
    def __init__(self, api_key: str = None, base_url: str = "https://openrouter.ai/api/v1"):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key=self.api_key,
        )
        self.model = os.getenv("ACR_MODEL", "openrouter/auto")

    async def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        if not self.api_key:
            return "ERROR: Missing OpenRouter API Key. Please set OPENROUTER_API_KEY environment variable."
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                extra_headers={
                    "HTTP-Referer": "https://github.com/tob/acr", # Optional
                    "X-Title": "Autobiographical Cognitive Runtime", # Optional
                }
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"ERROR: LLM Call failed: {str(e)}"
