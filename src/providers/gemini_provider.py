from typing import List, Dict, Any
import google.generativeai as genai
from ..models.base import AIModelInterface, AIMessage, AIResponse
import logging

logger = logging.getLogger(__name__)


class GeminiModel(AIModelInterface):
    """Google Gemini model implementation."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        api_key = config.get("api_key")
        if not api_key:
            raise ValueError("Gemini API key is required")

        genai.configure(api_key=api_key)
        self._model_name = config.get("model", "gemini-pro")

        # Initialize the model
        try:
            self.model = genai.GenerativeModel(self._model_name)
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {str(e)}")
            raise

    async def generate_response(
        self, 
        messages: List[AIMessage], 
        **kwargs
    ) -> AIResponse:
        """Generate response using Gemini API."""
        try:
            # Convert messages to Gemini format
            # Gemini uses a different conversation format
            conversation_parts = []

            for msg in messages:
                if msg.role == "system":
                    # System messages are handled as part of the prompt
                    conversation_parts.append(f"System: {msg.content}")
                elif msg.role == "user":
                    conversation_parts.append(f"User: {msg.content}")
                elif msg.role == "assistant":
                    conversation_parts.append(f"Assistant: {msg.content}")

            # Combine all parts into a single prompt
            prompt = "\n".join(conversation_parts)
            if not prompt.endswith("Assistant:"):
                prompt += "\nAssistant:"

            # Generate response
            generation_config = genai.types.GenerationConfig(
                temperature=kwargs.get("temperature", 0.7),
                max_output_tokens=kwargs.get("max_tokens", 1000),
                top_p=kwargs.get("top_p", 0.9),
                top_k=kwargs.get("top_k", 40),
            )

            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )

            if not response.text:
                raise ValueError("Empty response from Gemini")

            # Calculate token usage (approximate)
            prompt_tokens = len(prompt.split())
            completion_tokens = len(response.text.split())

            return AIResponse(
                content=response.text.strip(),
                model=self._model_name,
                usage={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens
                },
                metadata={
                    "finish_reason": "stop",
                    "safety_ratings": response.candidates[0].safety_ratings if response.candidates else None
                }
            )

        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise

    async def health_check(self) -> bool:
        """Check Gemini API health."""
        try:
            # Simple test generation
            response = self.model.generate_content("Hello")
            return bool(response.text)
        except Exception as e:
            logger.error(f"Gemini health check failed: {str(e)}")
            return False

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def provider(self) -> str:
        return "gemini"
