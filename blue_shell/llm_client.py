from __future__ import annotations

from typing import Any

from click import UsageError

from .config import cfg
from .llm_clients import (
    AnthropicClient,
    BedrockClient,
    LiteLLMClient,
    MistralClient,
    OllamaClient,
    OpenAIClient,
    OpenRouterClient,
)


class LLMClient:
    """Client responsible for providing LLM completions across providers."""

    def __init__(self) -> None:
        self.request_timeout = int(cfg.get("REQUEST_TIMEOUT"))

        def _get(key: str) -> str:
            try:
                return cfg.get(key)
            except UsageError:
                return ""

        self.clients = {
            "openai": OpenAIClient(
                cfg.get("OPENAI_API_KEY"), cfg.get("API_BASE_URL"), self.request_timeout
            ),
            "openrouter": OpenRouterClient(_get("OPENROUTER_API_KEY"), self.request_timeout),
            "ollama": OllamaClient(
                _get("OLLAMA_API_KEY"), _get("OLLAMA_API_BASE"), self.request_timeout
            ),
            "litellm": LiteLLMClient(
                _get("LITELLM_API_KEY"), _get("LITELLM_API_BASE"), self.request_timeout
            ),
            "anthropic": AnthropicClient(_get("ANTHROPIC_API_KEY"), self.request_timeout),
            "mistral": MistralClient(_get("MISTRAL_API_KEY"), self.request_timeout),
            "bedrock": BedrockClient(
                _get("AWS_ACCESS_KEY_ID"),
                _get("AWS_SECRET_ACCESS_KEY"),
                _get("AWS_REGION"),
                self.request_timeout,
            ),
        }

    def completion(self, model: str, **kwargs: Any) -> Any:
        default_provider = cfg.get("DEFAULT_PROVIDER")
        provider, model_name = (
            model.split("/", 1) if "/" in model else (default_provider, model)
        )
        client = self.clients.get(provider)
        if not client:
            raise UsageError(f"Unsupported provider '{provider}'")
        return client.completion(model_name, **kwargs)


def get_llm_client() -> LLMClient:
    """Factory returning configured ``LLMClient`` instance."""

    return LLMClient()
