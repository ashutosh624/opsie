from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from typing import Dict, Any
import re
import logging

from ..agent.ai_agent import AIAgent
from ..config import config

logger = logging.getLogger(__name__)


class SlackBot:
    """Slack bot implementation using Bolt for Python."""
    
    def __init__(self):
        # Initialize Slack app
        self.app = AsyncApp(
            token=config.slack_bot_token,
            signing_secret=config.slack_signing_secret
        )
        
        # Initialize AI agent
        self.ai_agent = AIAgent()
        
        # Register event handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register Slack event handlers."""
        
        @self.app.message("hello")
        async def handle_hello(message, say):
            """Handle hello messages."""
            user_id = message["user"]
            await say(f"Hello <@{user_id}>! I'm your AI assistant. How can I help you today?")
        
        @self.app.message(re.compile(r"^switch to (\w+)"))
        async def handle_model_switch(message, say):
            """Handle model switching commands."""
            user_id = message["user"]
            match = re.search(r"^switch to (\w+)", message["text"])
            
            if match:
                provider = match.group(1).lower()
                available_providers = self.ai_agent.get_available_providers()
                
                if provider in available_providers:
                    try:
                        # Process a dummy message to switch the model
                        await self.ai_agent.process_message(
                            user_id, "hello", provider=provider
                        )
                        model_info = self.ai_agent.get_current_model_info()
                        await say(f"✅ Switched to {provider} model: {model_info['model']}")
                    except Exception as e:
                        await say(f"❌ Failed to switch to {provider}: {str(e)}")
                else:
                    await say(f"❌ Unknown provider: {provider}. Available: {', '.join(available_providers)}")
        
        @self.app.message("models")
        async def handle_models_list(message, say):
            """Handle request to list available models."""
            available_providers = self.ai_agent.get_available_providers()
            current_model = self.ai_agent.get_current_model_info()
            
            response = f"🤖 **Available AI Models:**\n"
            for provider in available_providers:
                emoji = "✅" if provider == current_model["provider"] else "⚪"
                response += f"{emoji} {provider}\n"
            
            response += f"\n**Current Model:** {current_model['provider']} - {current_model['model']}"
            response += f"\n\n**Commands:**\n"
            response += f"• `switch to <provider>` - Switch AI model\n"
            response += f"• `clear` - Clear conversation history\n"
            response += f"• `health` - Check model health\n"
            response += f"• `models` - Show this list"
            
            await say(response)
        
        @self.app.message("clear")
        async def handle_clear_conversation(message, say):
            """Handle clear conversation command."""
            user_id = message["user"]
            await self.ai_agent.clear_conversation(user_id)
            await say("🗑️ Conversation history cleared!")
        
        @self.app.message("health")
        async def handle_health_check(message, say):
            """Handle health check command."""
            health_status = await self.ai_agent.health_check()
            
            if health_status["status"] == "healthy":
                await say(f"✅ Model is healthy: {health_status['provider']} - {health_status['model']}")
            else:
                await say(f"❌ Model health check failed: {health_status.get('message', 'Unknown error')}")
        
        @self.app.event("app_mention")
        async def handle_app_mention(event, say):
            """Handle app mentions."""
            user_id = event["user"]
            text = event["text"]
            
            # Remove bot mention from text
            text = re.sub(r"<@\w+>", "", text).strip()
            
            if text:
                response = await self.ai_agent.process_message(user_id, text)
                await say(response)
            else:
                await say("Hello! How can I help you today?")
        
        @self.app.message("")
        async def handle_direct_message(message, say):
            """Handle direct messages to the bot."""
            # Only respond to direct messages (not channel messages)
            if message.get("channel_type") == "im":
                user_id = message["user"]
                text = message["text"]
                
                # Skip if it's a command we've already handled
                if any(cmd in text.lower() for cmd in ["hello", "switch to", "models", "clear", "health"]):
                    return
                
                response = await self.ai_agent.process_message(user_id, text)
                await say(response)
    
    async def start(self):
        """Start the Slack bot."""
        if not config.validate_required_config():
            raise ValueError("Missing required Slack configuration. Please check your .env file.")
        
        # Use Socket Mode for development
        if config.slack_app_token:
            handler = AsyncSocketModeHandler(self.app, config.slack_app_token)
            await handler.start_async()
        else:
            # For production, you would typically use HTTP mode
            # This requires setting up proper webhooks and running on a public URL
            logger.warning("No app token provided. Socket mode not available.")
            raise ValueError("App token required for Socket Mode. Please set SLACK_APP_TOKEN in your .env file.")
    
    def get_app(self):
        """Get the Slack app instance for external use."""
        return self.app
