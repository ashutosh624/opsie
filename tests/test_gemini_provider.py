import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.providers.gemini_provider import GeminiModel
from src.models.base import AIMessage, AIResponse


class MockGeminiResponse:
    """Mock response from Gemini API."""
    def __init__(self, text="Mock response"):
        self.text = text
        self.candidates = [Mock()]
        self.candidates[0].safety_ratings = []


@pytest.fixture
def gemini_config():
    """Configuration for Gemini provider."""
    return {
        "api_key": "test-api-key",
        "model": "gemini-pro"
    }


@patch('google.generativeai.configure')
@patch('google.generativeai.GenerativeModel')
def test_gemini_model_init(mock_model_class, mock_configure, gemini_config):
    """Test Gemini model initialization."""
    mock_model_instance = Mock()
    mock_model_class.return_value = mock_model_instance
    
    model = GeminiModel(gemini_config)
    
    assert model.provider == "gemini"
    assert model.model_name == "gemini-pro"
    mock_configure.assert_called_once_with(api_key="test-api-key")
    mock_model_class.assert_called_once_with("gemini-pro")


@patch('google.generativeai.configure')
@patch('google.generativeai.GenerativeModel')
@pytest.mark.asyncio
async def test_gemini_generate_response(mock_model_class, mock_configure, gemini_config):
    """Test Gemini response generation."""
    mock_model_instance = Mock()
    mock_response = MockGeminiResponse("Hello! How can I help you?")
    mock_model_instance.generate_content.return_value = mock_response
    mock_model_class.return_value = mock_model_instance
    
    model = GeminiModel(gemini_config)
    
    messages = [
        AIMessage(role="user", content="Hello")
    ]
    
    response = await model.generate_response(messages)
    
    assert isinstance(response, AIResponse)
    assert response.content == "Hello! How can I help you?"
    assert response.model == "gemini-pro"
    assert response.usage["total_tokens"] > 0
    mock_model_instance.generate_content.assert_called_once()


@patch('google.generativeai.configure')
@patch('google.generativeai.GenerativeModel')
@pytest.mark.asyncio
async def test_gemini_health_check(mock_model_class, mock_configure, gemini_config):
    """Test Gemini health check."""
    mock_model_instance = Mock()
    mock_response = MockGeminiResponse("Health check response")
    mock_model_instance.generate_content.return_value = mock_response
    mock_model_class.return_value = mock_model_instance
    
    model = GeminiModel(gemini_config)
    
    health = await model.health_check()
    
    assert health is True
    mock_model_instance.generate_content.assert_called_once_with("Hello")


@patch('google.generativeai.configure')
@patch('google.generativeai.GenerativeModel')
@pytest.mark.asyncio
async def test_gemini_health_check_failure(mock_model_class, mock_configure, gemini_config):
    """Test Gemini health check failure."""
    mock_model_instance = Mock()
    mock_model_instance.generate_content.side_effect = Exception("API Error")
    mock_model_class.return_value = mock_model_instance
    
    model = GeminiModel(gemini_config)
    
    health = await model.health_check()
    
    assert health is False


def test_gemini_model_missing_api_key():
    """Test Gemini model initialization without API key."""
    config = {"model": "gemini-pro"}  # Missing api_key
    
    with pytest.raises(ValueError, match="Gemini API key is required"):
        GeminiModel(config)
