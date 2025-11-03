from .openai_client import OpenAIClient


class OllamaClient(OpenAIClient):
    def __init__(self, api_key: str, api_base: str | None, timeout: int) -> None:
        super().__init__(api_key or "ollama", api_base, timeout)
