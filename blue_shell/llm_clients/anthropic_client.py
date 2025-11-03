from __future__ import annotations

from typing import Any, Generator

from .base import BaseClient


class AnthropicClient(BaseClient):
    def __init__(self, api_key: str, timeout: int) -> None:
        self.api_key = api_key
        self.timeout = timeout
        self._client = None

    def _get_client(self):
        if self._client is None:
            import anthropic  # type: ignore

            self._client = anthropic.Anthropic(
                api_key=self.api_key, timeout=self.timeout
            )
        return self._client

    def completion(self, model: str, **kwargs: Any):
        client = self._get_client()

        def gen() -> Generator[dict[str, Any], None, None]:
            with client.messages.stream(
                model=model,
                messages=kwargs["messages"],
                temperature=kwargs.get("temperature"),
                top_p=kwargs.get("top_p"),
                max_tokens=1024,
            ) as stream:
                for event in stream:
                    if (
                        event.type == "content_block_delta"
                        and event.delta.type == "text_delta"
                    ):
                        yield {
                            "choices": [
                                {
                                    "delta": {"content": event.delta.text},
                                    "finish_reason": None,
                                }
                            ]
                        }

        return gen()
