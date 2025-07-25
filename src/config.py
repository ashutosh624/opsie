import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from .constants import GeminiConstants

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration."""
    
    # Slack Configuration
    slack_bot_token: str = os.getenv("SLACK_BOT_TOKEN", "")
    slack_signing_secret: str = os.getenv("SLACK_SIGNING_SECRET", "")
    slack_app_token: str = os.getenv("SLACK_APP_TOKEN", "")
    
    # AI Model Configuration
    default_ai_provider: str = os.getenv("DEFAULT_AI_PROVIDER", "openai")
    
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # Anthropic Configuration
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
    
    # Gemini Configuration
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", GeminiConstants.DEFAULT_MODEL)
    
    # Local Model Configuration
    local_model_path: str = os.getenv("LOCAL_MODEL_PATH", "microsoft/DialoGPT-medium")
    local_model_type: str = os.getenv("LOCAL_MODEL_TYPE", "huggingface")
    
    # Server Configuration
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "3000"))
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    def get_model_config(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """Get configuration for a specific AI model provider."""
        provider = provider or self.default_ai_provider
        
        if provider == "openai":
            return {
                "api_key": self.openai_api_key,
                "model": self.openai_model
            }
        elif provider == "anthropic":
            return {
                "api_key": self.anthropic_api_key,
                "model": self.anthropic_model
            }
        elif provider in ["gemini", "google"]:
            return {
                "api_key": self.gemini_api_key,
                "model": self.gemini_model
            }
        elif provider in ["local", "huggingface"]:
            return {
                "model_path": self.local_model_path,
                "model_name": self.local_model_path.split("/")[-1]
            }
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def validate_required_config(self) -> bool:
        """Validate that required configuration is present."""
        if not self.slack_bot_token or not self.slack_signing_secret:
            return False
        
        provider = self.default_ai_provider
        if provider == "openai" and not self.openai_api_key:
            return False
        elif provider == "anthropic" and not self.anthropic_api_key:
            return False
        elif provider in ["gemini", "google"] and not self.gemini_api_key:
            return False
        
        return True


# Global configuration instance
config = Config()
