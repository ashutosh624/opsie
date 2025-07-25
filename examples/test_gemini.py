"""
Example: Using Google Gemini Provider

This example demonstrates how to use the Google Gemini provider
in the AI Agent Slack Bot.
"""

import asyncio
import os
from src.providers.gemini_provider import GeminiModel
from src.models.base import AIMessage
from src.config import config

async def test_gemini_provider():
    """Test the Gemini provider with example conversations."""
    
    # Check if API key is available
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("⚠️  GEMINI_API_KEY not found in environment variables")
        print("Please set your Gemini API key in the .env file")
        return
    
    print("🤖 Testing Google Gemini Provider...")
    
    # Initialize Gemini model
    gemini_config = {
        "api_key": api_key,
        "model": "gemini-pro"
    }
    
    try:
        model = GeminiModel(gemini_config)
        print(f"✅ Initialized {model.provider} model: {model.model_name}")
        
        # Test health check
        print("\n🔍 Testing health check...")
        is_healthy = await model.health_check()
        print(f"Health status: {'✅ Healthy' if is_healthy else '❌ Unhealthy'}")
        
        if not is_healthy:
            return
        
        # Test conversation
        print("\n💬 Testing conversation...")
        
        messages = [
            AIMessage(role="system", content="You are a helpful AI assistant."),
            AIMessage(role="user", content="What can you tell me about artificial intelligence?")
        ]
        
        response = await model.generate_response(
            messages,
            temperature=0.7,
            max_tokens=200
        )
        
        print(f"User: {messages[1].content}")
        print(f"Gemini: {response.content}")
        print(f"\nModel: {response.model}")
        print(f"Usage: {response.usage}")
        
        # Test follow-up question
        print("\n💬 Testing follow-up...")
        
        messages.append(AIMessage(role="assistant", content=response.content))
        messages.append(AIMessage(role="user", content="Can you give me a specific example?"))
        
        response2 = await model.generate_response(
            messages,
            temperature=0.7,
            max_tokens=200
        )
        
        print(f"User: {messages[3].content}")
        print(f"Gemini: {response2.content}")
        
    except Exception as e:
        print(f"❌ Error testing Gemini provider: {str(e)}")


async def compare_providers():
    """Compare responses from different providers."""
    
    print("\n🔍 Comparing AI Providers...")
    
    question = "Explain machine learning in simple terms."
    messages = [AIMessage(role="user", content=question)]
    
    providers_to_test = []
    
    # Check available providers
    if os.getenv("GEMINI_API_KEY"):
        providers_to_test.append(("gemini", {
            "api_key": os.getenv("GEMINI_API_KEY"),
            "model": "gemini-pro"
        }))
    
    if os.getenv("OPENAI_API_KEY"):
        from src.providers.openai_provider import OpenAIModel
        providers_to_test.append(("openai", {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model": "gpt-3.5-turbo"
        }))
    
    print(f"\nQuestion: {question}\n")
    
    for provider_name, provider_config in providers_to_test:
        try:
            if provider_name == "gemini":
                model = GeminiModel(provider_config)
            elif provider_name == "openai":
                from src.providers.openai_provider import OpenAIModel
                model = OpenAIModel(provider_config)
            else:
                continue
            
            response = await model.generate_response(messages, max_tokens=150)
            
            print(f"🤖 {provider_name.upper()}:")
            print(f"{response.content}\n")
            
            tokens_used = "N/A"
            if response.usage and "total_tokens" in response.usage:
                tokens_used = response.usage["total_tokens"]
            print(f"Tokens used: {tokens_used}\n")
            print("-" * 50 + "\n")
            
        except Exception as e:
            print(f"❌ Error with {provider_name}: {str(e)}\n")


if __name__ == "__main__":
    print("Google Gemini Provider Example")
    print("=" * 40)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run tests
    asyncio.run(test_gemini_provider())
    asyncio.run(compare_providers())
