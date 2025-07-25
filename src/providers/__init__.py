from typing import Dict, Any
from .openai_provider import OpenAIModel
from .anthropic_provider import AnthropicModel
from .local_provider import LocalHuggingFaceModel
from .gemini_provider import GeminiModel
from ..models.base import AIModelInterface
import logging

logger = logging.getLogger(__name__)


class ModelFactory:
    """Factory class for creating AI model instances."""

    _providers = {
        "openai": OpenAIModel,
        "anthropic": AnthropicModel,
        # "local": LocalHuggingFaceModel,
        "huggingface": LocalHuggingFaceModel,  # Alias for local
        "gemini": GeminiModel,
        # "google": GeminiModel,  # Alias for gemini
    }

    @classmethod
    def create_model(cls, provider: str, config: Dict[str, Any]) -> AIModelInterface:
        """Create an AI model instance based on provider and configuration."""
        if provider not in cls._providers:
            raise ValueError(f"Unknown provider: {provider}. Available providers: {list(cls._providers.keys())}")

        try:
            model_class = cls._providers[provider]
            return model_class(config)
        except Exception as e:
            logger.error(f"Failed to create model for provider '{provider}': {str(e)}")
            raise

    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Get list of available model providers."""
        return list(cls._providers.keys())

    @classmethod
    def register_provider(cls, name: str, model_class: type) -> None:
        """Register a new model provider."""
        if not issubclass(model_class, AIModelInterface):
            raise ValueError("Model class must inherit from AIModelInterface")

        cls._providers[name] = model_class
        logger.info(f"Registered new model provider: {name}")
