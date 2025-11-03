from __future__ import annotations

import json
from typing import Any, Generator

from .base import BaseClient


class BedrockClient(BaseClient):
    def __init__(self, aws_key: str, aws_secret: str, region: str, timeout: int) -> None:
        self.aws_key = aws_key
        self.aws_secret = aws_secret
        self.region = region or "us-east-1"
        self.timeout = timeout
        self._client = None

    def _get_client(self):
        if self._client is None:
            import boto3  # type: ignore

            self._client = boto3.client(
                "bedrock-runtime",
                region_name=self.region,
                aws_access_key_id=self.aws_key or None,
                aws_secret_access_key=self.aws_secret or None,
            )
        return self._client

    def completion(self, model: str, **kwargs: Any):
        br = self._get_client()
        payload = {
            "messages": kwargs["messages"],
            "temperature": kwargs.get("temperature"),
            "top_p": kwargs.get("top_p"),
            "max_tokens": 1024,
        }
        response = br.invoke_model_with_response_stream(
            modelId=model, body=json.dumps(payload)
        )

        def gen() -> Generator[dict[str, Any], None, None]:
            for event in response.get("body"):
                if "chunk" in event:
                    data = json.loads(event["chunk"]["bytes"])
                    text = data.get("outputText") or data.get("completion", "")
                    if text:
                        yield {
                            "choices": [
                                {
                                    "delta": {"content": text},
                                    "finish_reason": None,
                                }
                            ]
                        }

        return gen()
