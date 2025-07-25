"""
Example: Adding a Custom AI Provider

This example shows how to add a new AI provider to the system.
In this case, we'll create a simple mock provider for demonstration.
"""

from typing import List, Dict, Any
from src.models.base import AIModelInterface, AIMessage, AIResponse
from src.providers import ModelFactory
import logging

logger = logging.getLogger(__name__)


class MockAIProvider(AIModelInterface):
    """Example mock AI provider for demonstration."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._model_name = config.get("model", "mock-gpt-4")
        self.responses = [
            "Hello! I'm a mock AI assistant.",
            "That's an interesting question!",
            "I'm here to help you with whatever you need.",
            "Let me think about that...",
            "Great question! Here's what I think..."
        ]
        self.response_index = 0
    
    async def generate_response(
        self, 
        messages: List[AIMessage], 
        **kwargs
    ) -> AIResponse:
        """Generate a mock response."""
        try:
            # Cycle through predefined responses
            response_text = self.responses[self.response_index % len(self.responses)]
            self.response_index += 1
            
            # Add some context from the last user message if available
            user_messages = [msg for msg in messages if msg.role == "user"]
            if user_messages:
                last_message = user_messages[-1].content
                response_text += f" (You asked about: {last_message[:50]}...)"
            
            return AIResponse(
                content=response_text,
                model=self._model_name,
                usage={
                    "prompt_tokens": sum(len(msg.content.split()) for msg in messages),
                    "completion_tokens": len(response_text.split()),
                    "total_tokens": sum(len(msg.content.split()) for msg in messages) + len(response_text.split())
                },
                metadata={"mock": True}
            )
            
        except Exception as e:
            logger.error(f"Mock provider error: {str(e)}")
            raise
    
    async def health_check(self) -> bool:
        """Mock health check - always returns True."""
        return True
    
    @property
    def model_name(self) -> str:
        return self._model_name
    
    @property
    def provider(self) -> str:
        return "mock"


def register_mock_provider():
    """Register the mock provider with the ModelFactory."""
    ModelFactory.register_provider("mock", MockAIProvider)
    print("✅ Mock provider registered!")


if __name__ == "__main__":
    # Example usage:
    import asyncio
    from src.config import config
    
    # Register the provider
    register_mock_provider()
    
    # Create an instance
    mock_config = {"model": "mock-gpt-4-turbo"}
    provider = MockAIProvider(mock_config)
    
    # Test it
    async def test_mock_provider():
        messages = [
            AIMessage(role="user", content="Hello, how are you?"),
        ]
        
        response = await provider.generate_response(messages)
        print(f"Response: {response.content}")
        print(f"Model: {response.model}")
        print(f"Usage: {response.usage}")
        
        health = await provider.health_check()
        print(f"Health: {health}")
    
    asyncio.run(test_mock_provider())
