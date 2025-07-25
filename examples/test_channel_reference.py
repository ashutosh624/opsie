"""
Quick test to verify the software engineering triage functionality
with channel description reference behavior.
"""

import asyncio
from unittest.mock import Mock, AsyncMock
from src.agent.ai_agent import AIAgent
from src.models.base import AIMessage, AIResponse


async def test_channel_description_reference():
    """Test that the bot references channel description for debugging format."""
    
    print("🔍 Testing Channel Description Reference...")
    
    # Create a mock AI model
    mock_model = Mock()
    mock_model.provider = "test"
    mock_model.model_name = "test-model"
    
    # Mock response that should reference channel description
    mock_model.generate_response = AsyncMock(
        return_value=AIResponse(
            content="Mock triage response referencing channel description format",
            model="test-model"
        )
    )
    
    # Create AI agent
    agent = AIAgent("test")
    agent.current_model = mock_model
    
    # Simulate incomplete issue report
    thread_context = [
        {
            "user_id": "engineer1",
            "text": "Something is broken, please help!",
            "timestamp": "1642259600.456"
        }
    ]
    
    # Channel info with description
    channel_info = {
        "name": "support-tickets",
        "description": "Support channel. Please follow the debugging format: include severity, steps to reproduce, environment details, and error logs.",
        "topic": "Customer support and bug reports"
    }
    
    # Process the message
    response = await agent.process_thread_message(
        user_id="engineer1",
        message="@bot Please help with this issue",
        thread_context=thread_context,
        channel_info=channel_info
    )
    
    # Verify the model was called
    mock_model.generate_response.assert_called_once()
    call_args = mock_model.generate_response.call_args[1]["messages"]
    
    # Check the system prompt
    system_message = call_args[0]
    assert system_message.role == "system"
    
    # Verify it references channel description without including the full format
    system_content = system_message.content
    assert "channel description" in system_content.lower()
    assert "debugging format" in system_content.lower()
    assert "#support-tickets" in system_content
    
    # Verify it contains the standard format structure within the codebase
    assert "🔍 **Issue Summary**" in system_content
    assert "📝 **Problem Description**" in system_content
    assert "🔄 **Steps to Reproduce**" in system_content
    assert "✅ **Expected Behavior**" in system_content
    assert "❌ **Actual Behavior**" in system_content
    assert "🖥️ **Environment Details**" in system_content
    assert "📋 **Error Messages/Logs**" in system_content
    
    # Verify it doesn't include the actual channel description content
    assert "include severity, steps to reproduce" not in system_content
    
    print("✅ Channel description reference test passed!")
    print(f"📋 System prompt correctly references channel description without including full content")


if __name__ == "__main__":
    print("Channel Description Reference Test")
    print("=" * 40)
    
    asyncio.run(test_channel_description_reference())
    
    print("\n🎉 Test passed!")
    print("\n📋 Key Features Verified:")
    print("• ✅ References channel description for debugging format")
    print("• ✅ Includes standard format structure in codebase") 
    print("• ✅ Doesn't pull actual description content into prompts")
    print("• ✅ Guides engineers to check channel description for complete format")
