import pytest
from unittest.mock import Mock
from src.models.base import AIMessage, AIResponse, AIModelInterface


def test_ai_message_creation():
    """Test AIMessage model creation."""
    message = AIMessage(role="user", content="Hello")
    
    assert message.role == "user"
    assert message.content == "Hello"
    assert message.metadata is None


def test_ai_message_with_metadata():
    """Test AIMessage with metadata."""
    metadata = {"timestamp": "2023-01-01"}
    message = AIMessage(role="user", content="Hello", metadata=metadata)
    
    assert message.metadata == metadata


def test_ai_response_creation():
    """Test AIResponse model creation."""
    response = AIResponse(
        content="Hello back!",
        model="gpt-4",
        usage={"tokens": 10}
    )
    
    assert response.content == "Hello back!"
    assert response.model == "gpt-4"
    assert response.usage == {"tokens": 10}


def test_ai_model_interface_is_abstract():
    """Test that AIModelInterface cannot be instantiated directly."""
    with pytest.raises(TypeError):
        AIModelInterface({})


class MockAIModel(AIModelInterface):
    """Mock implementation for testing."""
    
    def __init__(self, config):
        super().__init__(config)
    
    async def generate_response(self, messages, **kwargs):
        return AIResponse(content="mock response", model="mock")
    
    async def health_check(self):
        return True
    
    @property
    def model_name(self):
        return "mock-model"
    
    @property
    def provider(self):
        return "mock"


@pytest.mark.asyncio
async def test_mock_ai_model():
    """Test mock AI model implementation."""
    model = MockAIModel({"test": "config"})
    
    assert model.provider == "mock"
    assert model.model_name == "mock-model"
    
    messages = [AIMessage(role="user", content="test")]
    response = await model.generate_response(messages)
    
    assert response.content == "mock response"
    assert response.model == "mock"
    
    health = await model.health_check()
    assert health is True
