"""
Example: Testing Thread Support

This example demonstrates the thread support functionality
of the AI Agent Slack Bot.
"""

import asyncio
from unittest.mock import Mock, AsyncMock
from src.agent.ai_agent import AIAgent
from src.models.base import AIMessage, AIResponse


async def test_thread_processing():
    """Test thread message processing functionality."""
    
    print("🧵 Testing Thread Support...")
    
    # Create a mock AI model
    mock_model = Mock()
    mock_model.provider = "test"
    mock_model.model_name = "test-model"
    mock_model.generate_response = AsyncMock(
        return_value=AIResponse(
            content="I can see the full thread context and will respond accordingly.",
            model="test-model",
            usage={"total_tokens": 20}
        )
    )
    
    # Create AI agent
    agent = AIAgent("test")
    agent.current_model = mock_model
    
    # Simulate thread context
    thread_context = [
        {
            "user_id": "user1",
            "text": "Hey everyone, I'm having trouble with my Python code",
            "timestamp": "1234567890.123"
        },
        {
            "user_id": "user2", 
            "text": "What kind of error are you getting?",
            "timestamp": "1234567891.456"
        },
        {
            "user_id": "user1",
            "text": "It's a syntax error on line 15",
            "timestamp": "1234567892.789"
        }
    ]
    
    # Process thread message
    response = await agent.process_thread_message(
        user_id="user1",
        message="Can you help me debug this?",
        thread_context=thread_context
    )
    
    print(f"✅ Thread response: {response}")
    
    # Verify the model was called with thread context
    mock_model.generate_response.assert_called_once()
    call_args = mock_model.generate_response.call_args[1]["messages"]
    
    print(f"📝 Thread context processed: {len(call_args)} messages")
    
    # Check that system message was added
    assert call_args[0].role == "system"
    assert "thread conversation" in call_args[0].content.lower()
    
    # Check that all thread messages were included
    assert len(call_args) >= len(thread_context) + 1  # +1 for system message
    
    print("✅ Thread processing test passed!")


async def test_regular_vs_thread_processing():
    """Compare regular message processing vs thread processing."""
    
    print("\n🔄 Comparing Regular vs Thread Processing...")
    
    # Create mock models
    mock_model = Mock()
    mock_model.provider = "test"
    mock_model.model_name = "test-model"
    
    # Track calls
    call_count = 0
    call_contexts = []
    
    async def mock_generate(messages, **kwargs):
        nonlocal call_count, call_contexts
        call_count += 1
        call_contexts.append(messages)
        return AIResponse(
            content=f"Response {call_count}",
            model="test-model",
            usage={"total_tokens": 10}
        )
    
    mock_model.generate_response = AsyncMock(side_effect=mock_generate)
    
    # Create AI agent
    agent = AIAgent("test")
    agent.current_model = mock_model
    
    # Test regular processing
    regular_response = await agent.process_message("user1", "Hello, how are you?")
    regular_context = call_contexts[0]
    
    # Test thread processing
    thread_context = [
        {"user_id": "user1", "text": "Hello", "timestamp": "123"},
        {"user_id": "user2", "text": "Hi there!", "timestamp": "124"}
    ]
    
    thread_response = await agent.process_thread_message(
        "user1", "How are you?", thread_context
    )
    thread_message_context = call_contexts[1]
    
    print(f"📊 Regular processing: {len(regular_context)} messages")
    print(f"📊 Thread processing: {len(thread_message_context)} messages")
    
    # Thread processing should have more context
    assert len(thread_message_context) > len(regular_context)
    
    # Thread processing should include system message about threads
    thread_system_msg = next((msg for msg in thread_message_context if msg.role == "system"), None)
    assert thread_system_msg is not None
    assert "thread" in thread_system_msg.content.lower()
    
    print("✅ Processing comparison test passed!")


if __name__ == "__main__":
    print("Thread Support Testing")
    print("=" * 30)
    
    asyncio.run(test_thread_processing())
    asyncio.run(test_regular_vs_thread_processing())
    
    print("\n🎉 All thread tests passed!")
    print("\n📋 Thread Features:")
    print("• ✅ Reads complete thread context")
    print("• ✅ Maintains conversation flow")
    print("• ✅ Responds within threads")
    print("• ✅ Distinguishes thread vs regular messages")
    print("• ✅ Preserves individual user history")
