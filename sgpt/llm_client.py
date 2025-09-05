from __future__ import annotations

from typing import Any, Callable

from .config import cfg


class LLMClient:
    """Client responsible for providing LLM completions."""

    def __init__(self) -> None:
        base_url = cfg.get("API_BASE_URL")
        self.use_litellm = cfg.get("USE_LITELLM") == "true"
        self.additional_kwargs: dict[str, Any] = {
            "timeout": int(cfg.get("REQUEST_TIMEOUT")),
            "api_key": cfg.get("OPENAI_API_KEY"),
            "base_url": None if base_url == "default" else base_url,
        }

        if self.use_litellm:
            import litellm  # type: ignore

            litellm.suppress_debug_info = True
            self.completion_fn: Callable[..., Any] = litellm.completion
            # LiteLLM uses environment variables for auth
            self.additional_kwargs.pop("api_key")
        else:
            from openai import OpenAI

            client = OpenAI(**self.additional_kwargs)  # type: ignore
            self.completion_fn = client.chat.completions.create
            # OpenAI client is preconfigured with kwargs above
            self.additional_kwargs = {}

    def completion(self, **kwargs: Any) -> Any:
        return self.completion_fn(**kwargs, **self.additional_kwargs)


def get_llm_client() -> LLMClient:
    """Factory returning configured ``LLMClient`` instance."""

    return LLMClient()
