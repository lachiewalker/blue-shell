from __future__ import annotations

from typing import Any

from .base import BaseClient


class OpenAIClient(BaseClient):
    def __init__(self, api_key: str, api_base: str | None, timeout: int) -> None:
        self.api_key = api_key
        self.api_base = api_base
        self.timeout = timeout
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI

            kwargs: dict[str, Any] = {"api_key": self.api_key, "timeout": self.timeout}
            if self.api_base and self.api_base != "default":
                kwargs["base_url"] = self.api_base
            self._client = OpenAI(**kwargs)
        return self._client

    def completion(self, model: str, **kwargs: Any):
        return self._get_client().chat.completions.create(model=model, **kwargs)
