from typing import List, Dict, Any, Optional
from ..models.base import AIModelInterface, AIMessage, AIResponse
from ..providers import ModelFactory
from ..config import config
from ..utils.prompt_loader import prompt_loader
import logging

logger = logging.getLogger(__name__)


class AIAgent:
    """Main AI agent that handles conversations and model switching."""

    def __init__(self, default_provider: Optional[str] = None):
        self.default_provider = default_provider or config.default_ai_provider
        self.current_model: Optional[AIModelInterface] = None
        self.conversation_history: Dict[str, List[AIMessage]] = {}

        # Initialize default model
        self._switch_model(self.default_provider)

    def _switch_model(self, provider: str) -> None:
        """Switch to a different AI model provider."""
        try:
            model_config = config.get_model_config(provider)
            self.current_model = ModelFactory.create_model(provider, model_config)
            logger.info(f"Switched to {provider} model: {self.current_model.model_name}")
        except Exception as e:
            logger.error(f"Failed to switch to {provider} model: {str(e)}")
            raise

    async def process_message(
        self,
        user_id: str,
        message: str,
        provider: Optional[str] = None,
        **kwargs
    ) -> str:
        """Process a user message and return AI response."""

        # Switch model if different provider requested
        if provider and self.current_model and provider != self.current_model.provider:
            self._switch_model(provider)

        # Get or create conversation history for user
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []

        # Add user message to history
        user_message = AIMessage(role="user", content=message)
        self.conversation_history[user_id].append(user_message)

        # Keep conversation history manageable (last 10 messages)
        if len(self.conversation_history[user_id]) > 10:
            self.conversation_history[user_id] = self.conversation_history[user_id][-10:]

        try:
            # Generate AI response
            if not self.current_model:
                raise RuntimeError("No AI model loaded")

            response = await self.current_model.generate_response(
                messages=self.conversation_history[user_id],
                **kwargs
            )

            # Add AI response to history
            ai_message = AIMessage(role="assistant", content=response.content)
            self.conversation_history[user_id].append(ai_message)

            return response.content

        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return "Sorry, I encountered an error while processing your message. Please try again."

    async def process_thread_message(
        self,
        user_id: str,
        message: str,
        thread_context: List[Dict[str, Any]],
        provider: Optional[str] = None,
        **kwargs
    ) -> str:
        """Process a message within a thread context with software engineering triage."""

        # Switch model if different provider requested
        if provider and self.current_model and provider != self.current_model.provider:
            self._switch_model(provider)

        # Build conversation from thread context
        thread_messages = []

        # Add specialized system message for software engineering triage
        system_prompt = self._build_software_engineer_prompt()
        thread_messages.append(AIMessage(role="system", content=system_prompt))

        # Convert thread context to AIMessage format
        for ctx_msg in thread_context:
            # Determine if this is from the current user or others
            role = "user" if ctx_msg["user_id"] == user_id else "user"
            thread_messages.append(AIMessage(
                role=role,
                content=ctx_msg["text"],
                metadata={"user_id": ctx_msg["user_id"], "timestamp": ctx_msg["timestamp"]}
            ))

        # Add the current message if it's not already in the context
        current_msg_text = message.strip()
        if not thread_context or thread_context[-1]["text"] != current_msg_text:
            thread_messages.append(AIMessage(role="user", content=current_msg_text))

        try:
            # Generate AI response with thread context
            if not self.current_model:
                raise RuntimeError("No AI model loaded")

            logger.info("Thread messages", thread_messages)

            response = await self.current_model.generate_response(
                messages=thread_messages,
                **kwargs
            )

            # Update conversation history for the user (maintaining individual history)
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []

            # Add current interaction to user's history
            user_message = AIMessage(role="user", content=message)
            ai_message = AIMessage(role="assistant", content=response.content)

            self.conversation_history[user_id].extend([user_message, ai_message])

            # Keep conversation history manageable
            if len(self.conversation_history[user_id]) > 10:
                self.conversation_history[user_id] = self.conversation_history[user_id][-10:]

            logger.info(response.content)

            return response.content

        except Exception as e:
            logger.error("Error generating thread response: %s", str(e))
            return "Sorry, I encountered an error while processing your message in this thread. Please try again."

    def _build_software_engineer_prompt(self) -> str:
        """Build a specialized system prompt for software engineering triage."""
        
        # Load base prompt from file
        base_prompt = prompt_loader.load_prompt("software_engineer_triage")
        
        if not base_prompt:
            # Fallback prompt if file loading fails
            logger.warning("Failed to load software engineer triage prompt, using fallback")
            base_prompt = """You are a Senior Software Engineer acting as a technical triage specialist in a Slack support thread. 
            Analyze technical issues, verify debugging information completeness, and provide technical insights."""

        return base_prompt

    async def clear_conversation(self, user_id: str) -> None:
        """Clear conversation history for a user."""
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]
            logger.info("Cleared conversation history for user %s", user_id)

    def get_available_providers(self) -> List[str]:
        """Get list of available AI model providers."""
        return ModelFactory.get_available_providers()

    def get_current_model_info(self) -> Dict[str, str]:
        """Get information about the currently active model."""
        if not self.current_model:
            return {"provider": "none", "model": "none"}

        return {
            "provider": self.current_model.provider,
            "model": self.current_model.model_name
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on current model."""
        if not self.current_model:
            return {"status": "error", "message": "No model loaded"}

        try:
            is_healthy = await self.current_model.health_check()
            return {
                "status": "healthy" if is_healthy else "unhealthy",
                "provider": self.current_model.provider,
                "model": self.current_model.model_name
            }
        except (ConnectionError, TimeoutError, ValueError) as e:
            return {
                "status": "error",
                "message": str(e),
                "provider": self.current_model.provider,
                "model": self.current_model.model_name
            }
