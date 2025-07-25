import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from src.agent.ai_agent import AIAgent
from src.models.base import AIMessage, AIResponse


@pytest.fixture
def mock_model():
    """Create a mock AI model for testing."""
    model = Mock()
    model.provider = "test"
    model.model_name = "test-model"
    model.generate_response = AsyncMock(
        return_value=AIResponse(
            content="Test response",
            model="test-model",
            usage={"total_tokens": 10}
        )
    )
    model.health_check = AsyncMock(return_value=True)
    return model


@pytest.fixture
def ai_agent(mock_model):
    """Create an AI agent with a mock model."""
    agent = AIAgent("test")
    agent.current_model = mock_model
    return agent


@pytest.mark.asyncio
async def test_process_message(ai_agent, mock_model):
    """Test basic message processing."""
    response = await ai_agent.process_message("user1", "Hello")
    
    assert response == "Test response"
    assert len(ai_agent.conversation_history["user1"]) == 2  # user + assistant
    mock_model.generate_response.assert_called_once()


@pytest.mark.asyncio
async def test_clear_conversation(ai_agent):
    """Test conversation clearing."""
    # Add some conversation history
    await ai_agent.process_message("user1", "Hello")
    assert "user1" in ai_agent.conversation_history
    
    # Clear conversation
    await ai_agent.clear_conversation("user1")
    assert "user1" not in ai_agent.conversation_history


@pytest.mark.asyncio
async def test_health_check(ai_agent, mock_model):
    """Test health check functionality."""
    health_status = await ai_agent.health_check()
    
    assert health_status["status"] == "healthy"
    assert health_status["provider"] == "test"
    assert health_status["model"] == "test-model"
    mock_model.health_check.assert_called_once()


@pytest.mark.asyncio
async def test_conversation_history_limit(ai_agent):
    """Test that conversation history is limited."""
    # Add more than 10 messages
    for i in range(12):
        await ai_agent.process_message("user1", f"Message {i}")
    
    # Should only keep last 10 messages
    assert len(ai_agent.conversation_history["user1"]) == 10


def test_get_current_model_info(ai_agent):
    """Test getting current model information."""
    model_info = ai_agent.get_current_model_info()
    
    assert model_info["provider"] == "test"
    assert model_info["model"] == "test-model"


def test_get_available_providers():
    """Test getting available providers."""
    from src.providers import ModelFactory
    
    providers = ModelFactory.get_available_providers()
    assert isinstance(providers, list)
    assert len(providers) > 0
