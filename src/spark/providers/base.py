"""Provider boundary limited to a connection test in Phase 1."""

from typing import Protocol


class LLMProvider(Protocol):
    def test_connection(self, api_key: str, model: str, timeout: float = 15.0) -> str: ...
