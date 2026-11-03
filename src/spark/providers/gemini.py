"""Gemini connection test with categorized SDK errors."""

import httpx
from google import genai
from google.genai import errors, types


def classify_exception(exc: Exception) -> str:
    """Map installed SDK and common transport exceptions to user-facing outcomes."""
    if isinstance(exc, (TimeoutError, httpx.TimeoutException)):
        return "The connection timed out. Check your network and try again."
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        message = str(exc).lower()
        if code == 401 or code == 403:
            if "region" in message or "location" in message or "not available" in message:
                return (
                    "Gemini is unavailable in this region or for this account. "
                    "Check Google's current availability."
                )
            return "Google rejected the API key. Check it in Settings."
        if code == 429:
            return "Gemini reported a quota or rate limit. Check your Google AI Studio account."
        if code == 404 or (
            "model" in message
            and any(
                marker in message
                for marker in (
                    "not found",
                    "unknown",
                    "unexpected model name format",
                    "unsupported model",
                )
            )
        ):
            return "The configured Gemini model was not found. Check the model name in Settings."
        if code in (400, 422) and ("location" in message or "region" in message):
            return (
                "Gemini is unavailable in this region or for this account. "
                "Check Google's current availability."
            )
        return "Gemini returned an unexpected error. See the log for details."
    if isinstance(exc, (ConnectionError, OSError, httpx.ConnectError, httpx.NetworkError)):
        return "Network unavailable. Check your connection and try again."
    return "Gemini connection test failed unexpectedly. See the log for details."


class GeminiProvider:
    def test_connection(self, api_key: str, model: str, timeout: float = 15.0) -> str:
        if not api_key:
            return "No Gemini API key is configured. Add one in Settings."
        if not model.strip():
            return "No Gemini model is configured. Set a model name in Settings first."
        try:
            http_options = types.HttpOptions(
                timeout=int(timeout * 1000),
                retry_options=types.HttpRetryOptions(attempts=1),
            )
            client = genai.Client(api_key=api_key, http_options=http_options)
            client.models.generate_content(model=model, contents="Reply with OK.")
            return "Gemini connection succeeded."
        except Exception as exc:
            raise ConnectionTestError(classify_exception(exc)) from exc


class ConnectionTestError(Exception):
    """A classified, safe-to-display connection test failure."""
