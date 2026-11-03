"""Small text channel interfaces for future channel implementations."""

from typing import Protocol


class InputChannel(Protocol):
    def receive(self, text: str) -> str: ...


class OutputChannel(Protocol):
    def send(self, text: str) -> None: ...


class TextChannel:
    """Minimal Phase 1 input/output channel connected to UI callbacks."""

    def __init__(self, handler, output):
        self._handler = handler
        self._output = output

    def receive(self, text: str) -> str:
        return self._handler(text)

    def send(self, text: str) -> None:
        self._output(text)
