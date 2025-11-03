from typing import Any

from .openai_client import OpenAIClient


class OpenRouterClient(OpenAIClient):
    def __init__(self, api_key: str, timeout: int) -> None:
        super().__init__(api_key, "https://openrouter.ai/api/v1", timeout)
