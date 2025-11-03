from typing import Any


class BaseClient:
    """Interface for provider-specific LLM clients."""

    def completion(self, model: str, **kwargs: Any):
        raise NotImplementedError
