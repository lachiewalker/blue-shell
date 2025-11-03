from __future__ import annotations

from typing import Any, Generator

from .base import BaseClient


class MistralClient(BaseClient):
    def __init__(self, api_key: str, timeout: int) -> None:
        self.api_key = api_key
        self.timeout = timeout
        self._client = None

    def _get_client(self):
        if self._client is None:
            from mistralai.client import MistralClient as SDK  # type: ignore

            self._client = SDK(api_key=self.api_key)
        return self._client

    def completion(self, model: str, **kwargs: Any):
        client = self._get_client()
        from mistralai.models.chat_completion import ChatMessage  # type: ignore

        def gen() -> Generator[dict[str, Any], None, None]:
            stream = client.chat_stream(
                model=model,
                messages=[
                    ChatMessage(role=m["role"], content=m["content"])
                    for m in kwargs["messages"]
                ],
                temperature=kwargs.get("temperature"),
                top_p=kwargs.get("top_p"),
            )
            for chunk in stream:
                delta = chunk.data[0].delta
                content = getattr(delta, "content", None)
                if content:
                    yield {
                        "choices": [
                            {
                                "delta": {"content": content},
                                "finish_reason": None,
                            }
                        ]
                    }

        return gen()
