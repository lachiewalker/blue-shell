from __future__ import annotations

from typing import Any

from .base import BaseClient


class LiteLLMClient(BaseClient):
    def __init__(self, api_key: str, api_base: str | None, timeout: int) -> None:
        self.api_key = api_key
        self.api_base = api_base
        self.timeout = timeout

    def completion(self, model: str, **kwargs: Any):
        import litellm  # type: ignore

        litellm.suppress_debug_info = True
        call_kwargs = {
            "model": model,
            **kwargs,
            "stream": True,
            "timeout": self.timeout,
        }
        if self.api_base:
            call_kwargs["api_base"] = self.api_base
        if self.api_key:
            call_kwargs["api_key"] = self.api_key
        return litellm.completion(**call_kwargs)
