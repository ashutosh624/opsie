import pytest
from unittest.mock import patch
from src.providers import ModelFactory
from src.providers.gemini_provider import GeminiModel


def test_model_factory_available_providers():
    """Test that ModelFactory includes all expected providers."""
    providers = ModelFactory.get_available_providers()
    
    expected_providers = ["openai", "anthropic", "local", "huggingface", "gemini", "google"]
    for provider in expected_providers:
        assert provider in providers


@patch('google.generativeai.configure')
@patch('google.generativeai.GenerativeModel')
def test_model_factory_create_gemini(mock_model_class, mock_configure):
    """Test creating Gemini model through ModelFactory."""
    config = {
        "api_key": "test-key",
        "model": "gemini-pro"
    }
    
    model = ModelFactory.create_model("gemini", config)
    
    assert isinstance(model, GeminiModel)
    assert model.provider == "gemini"


@patch('google.generativeai.configure')
@patch('google.generativeai.GenerativeModel')
def test_model_factory_create_google_alias(mock_model_class, mock_configure):
    """Test creating Gemini model using 'google' alias."""
    config = {
        "api_key": "test-key",
        "model": "gemini-pro"
    }
    
    model = ModelFactory.create_model("google", config)
    
    assert isinstance(model, GeminiModel)
    assert model.provider == "gemini"


def test_model_factory_unknown_provider():
    """Test error handling for unknown provider."""
    with pytest.raises(ValueError, match="Unknown provider: unknown"):
        ModelFactory.create_model("unknown", {})
