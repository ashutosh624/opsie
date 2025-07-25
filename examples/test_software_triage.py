"""
Example: Software Engineering Triage Bot

This example demonstrates how the AI bot acts as a software engineer
to triage issues and verify debugging format in Slack threads.
"""

import asyncio
import sys
import os
from unittest.mock import Mock, AsyncMock

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.ai_agent import AIAgent
from src.models.base import AIMessage, AIResponse


async def test_software_engineering_triage():
    """Test the software engineering triage functionality."""
    
    print("👨‍💻 Testing Software Engineering Triage Bot...")
    
    # Create a mock AI model
    mock_model = Mock()
    mock_model.provider = "test"
    mock_model.model_name = "test-model"
    
    # Mock response for triage analysis
    mock_model.generate_response = AsyncMock(
        return_value=AIResponse(
            content="""## 🔍 **TRIAGE ANALYSIS**

**Issue Severity**: HIGH - Authentication system affecting 50% of users
**Urgency**: IMMEDIATE - Customer-facing impact

## ✅ **Information Completeness Check**
Your report follows the debugging format well and includes:
- ✅ Clear problem description
- ✅ Steps to reproduce  
- ✅ Expected vs actual behavior
- ✅ Environment details
- ✅ Error messages/logs
- ✅ Timeline information

## 🔧 **Initial Analysis & Recommendations**

**Root Cause Hypothesis**: 
The timing suggests this is related to your recent deployment (v3.2.1 at 14:00 UTC). The JWT audience validation error indicates a configuration issue with OAuth settings.

**Immediate Actions**:
1. **Check OAuth Configuration**: Verify Google OAuth client ID and audience settings in the new deployment
2. **Compare Configurations**: Diff OAuth config between v3.2.0 and v3.2.1
3. **Rollback Option**: Consider rolling back to v3.2.0 if issue persists

**Next Steps**:
1. Check application logs for any OAuth configuration changes
2. Verify Google Developer Console settings haven't changed
3. Test OAuth flow in staging environment with v3.2.1

## 🚨 **Escalation Recommendation**
This should be escalated to the Platform Team immediately due to:
- High user impact (50% of users affected)
- Authentication system criticality
- Potential need for emergency rollback

Would you like me to help draft the escalation ticket or assist with any of these troubleshooting steps?""",
            model="test-model",
            usage={"total_tokens": 150}
        )
    )
    
    # Create AI agent
    agent = AIAgent("test")
    agent.current_model = mock_model
    
    # Simulate a well-formed issue report in thread
    thread_context = [
        {
            "user_id": "engineer1",
            "text": """🔍 **Issue Summary**
Title: User authentication failing for OAuth login
Severity: High
Impact: 50% of users unable to login via Google OAuth

📝 **Problem Description**
Since 2024-01-15 14:30 UTC, users attempting to login via Google OAuth are receiving "Invalid credentials" error. Username/password login works fine.

🔄 **Steps to Reproduce**
1. Go to login page
2. Click "Login with Google"  
3. Complete Google OAuth flow
4. Redirected back with error

✅ **Expected Behavior**
User should be logged in and redirected to dashboard

❌ **Actual Behavior**
Error message: "Authentication failed - Invalid credentials"

🖥️ **Environment Details**
- Operating System: Production servers (Ubuntu 20.04)
- Application Version: v3.2.1 (deployed 2024-01-15 14:00 UTC)
- Database: PostgreSQL 14.2

📋 **Error Messages/Logs**
[2024-01-15 14:32:15] ERROR: OAuth token validation failed
[2024-01-15 14:32:15] ERROR: Invalid audience in JWT token""",
            "timestamp": "1642259535.123"
        }
    ]
    
    # Channel info for context
    channel_info = {
        "name": "critical-incidents",
        "description": "For critical production issues. Please follow the debugging format: https://company.com/debugging-format. Include severity assessment and customer impact.",
        "topic": "Critical incident response channel",
        "purpose": "Emergency production issue escalation"
    }
    
    # Process the triage request
    response = await agent.process_thread_message(
        user_id="engineer1",
        message="@bot Can you help triage this issue?",
        thread_context=thread_context,
        channel_info=channel_info
    )
    
    print(f"🤖 **Triage Bot Response:**\n{response}")
    
    # Verify the model was called with engineering context
    mock_model.generate_response.assert_called_once()
    call_args = mock_model.generate_response.call_args[1]["messages"]
    
    # Check that specialized system prompt was used
    system_message = call_args[0]
    assert system_message.role == "system"
    assert "Senior Software Engineer" in system_message.content
    assert "triage specialist" in system_message.content
    assert "debugging format" in system_message.content
    
    print("✅ Software Engineering Triage test passed!")


async def test_incomplete_issue_report():
    """Test triage of an incomplete issue report."""
    
    print("\n🔍 Testing Incomplete Issue Report Handling...")
    
    # Create mock model for incomplete report response
    mock_model = Mock()
    mock_model.provider = "test"
    mock_model.model_name = "test-model"
    
    mock_model.generate_response = AsyncMock(
        return_value=AIResponse(
            content="""## ⚠️ **INCOMPLETE DEBUGGING INFORMATION**

I've reviewed your issue report and need additional information to provide effective triage.

## ❌ **Missing Required Information**:

1. **Environment Details**: Please specify:
   - Operating system and version
   - Application version
   - Browser (if web-based issue)
   - Any relevant dependency versions

2. **Steps to Reproduce**: The current description is too vague. Please provide:
   - Exact steps a engineer could follow to reproduce the issue
   - Any specific test data or conditions required

3. **Error Messages/Logs**: Please include:
   - Complete error messages (not just "something is broken")
   - Relevant log entries with timestamps
   - Stack traces if available

4. **Expected vs Actual Behavior**: Please clearly distinguish:
   - What you expected to happen
   - What actually happened instead

## 📋 **Debugging Format Reference**

Please refer to the debugging format outlined in the channel description for the complete template and guidelines.

The standard format should include:
- 🔍 Issue Summary (title, severity, impact)
- 📝 Problem Description (clear description with timeline)
- 🔄 Steps to Reproduce (numbered steps)
- ✅ Expected Behavior
- ❌ Actual Behavior  
- 🖥️ Environment Details
- 📋 Error Messages/Logs
- 🔧 Attempted Solutions

Once you provide this information following the format in the channel description, I can perform a proper triage analysis and recommend next steps.""",
            model="test-model",
            usage={"total_tokens": 120}
        )
    )
    
    # Create AI agent
    agent = AIAgent("test")
    agent.current_model = mock_model
    
    # Simulate incomplete issue report
    thread_context = [
        {
            "user_id": "engineer2",
            "text": "Hey, something is broken in production. Users are complaining. Can someone help?",
            "timestamp": "1642259600.456"
        }
    ]
    
    channel_info = {
        "name": "bug-reports",
        "description": "Bug reporting channel. Please use the standard debugging format: include steps to reproduce, environment details, and error messages.",
        "topic": "Bug reports and issue tracking"
    }
    
    # Process the incomplete report
    response = await agent.process_thread_message(
        user_id="engineer2",
        message="@bot Please help triage this",
        thread_context=thread_context,
        channel_info=channel_info
    )
    
    print(f"🤖 **Triage Bot Response:**\n{response}")
    print("✅ Incomplete report handling test passed!")


if __name__ == "__main__":
    print("Software Engineering Triage Bot Testing")
    print("=" * 50)
    
    asyncio.run(test_software_engineering_triage())
    asyncio.run(test_incomplete_issue_report())
    
    print("\n🎉 All triage tests passed!")
    print("\n📋 Triage Bot Features:")
    print("• ✅ Analyzes issue severity and impact")
    print("• ✅ Verifies debugging information completeness")
    print("• ✅ Guides proper format compliance")
    print("• ✅ Provides technical analysis and next steps")
    print("• ✅ Recommends escalation when needed")
    print("• ✅ Uses channel-specific context and guidelines")
