from unittest.mock import Mock

from google.genai import errors

from spark.providers.gemini import ConnectionTestError, GeminiProvider, classify_exception


def test_connection_test_no_key_and_no_model():
    provider = GeminiProvider()
    assert "No Gemini API key" in provider.test_connection("", "model")
    assert "No Gemini model" in provider.test_connection("key", "")


def test_provider_success(monkeypatch):
    models = Mock()
    models.generate_content.return_value = object()
    client = Mock(models=models)
    monkeypatch.setattr("spark.providers.gemini.genai.Client", Mock(return_value=client))
    assert GeminiProvider().test_connection("key", "chosen-model") == "Gemini connection succeeded."
    models.generate_content.assert_called_once_with(model="chosen-model", contents="Reply with OK.")


def test_sdk_error_mapping():
    assert (
        "rejected" in classify_exception(errors.APIError(401, {"message": "unauthorized"})).lower()
    )
    assert (
        "rejected"
        in classify_exception(
            errors.APIError(400, {"message": "API key not valid. Please pass a valid API key."})
        ).lower()
    )
    assert "quota" in classify_exception(errors.APIError(429, {"message": "limited"})).lower()
    assert (
        "not found"
        in classify_exception(errors.APIError(404, {"message": "model not found"})).lower()
    )
    assert "timed out" in classify_exception(TimeoutError()).lower()
    assert "network unavailable" in classify_exception(ConnectionError()).lower()


def test_all_documented_connection_categories():
    assert (
        "region"
        in classify_exception(errors.APIError(403, {"message": "location not available"})).lower()
    )
    assert "unexpected" in classify_exception(RuntimeError("unexpected")).lower()
    bad_model = errors.APIError(
        400,
        {"error": {"message": "GenerateContentRequest.model: unexpected model name format"}},
    )
    assert "model" in classify_exception(bad_model).lower()


def test_provider_raises_safe_classified_error(monkeypatch):
    monkeypatch.setattr(
        "spark.providers.gemini.genai.Client", Mock(side_effect=ConnectionError("offline"))
    )
    try:
        GeminiProvider().test_connection("key", "model")
    except ConnectionTestError as exc:
        assert "Network unavailable" in str(exc)
    else:
        raise AssertionError("expected classified failure")
