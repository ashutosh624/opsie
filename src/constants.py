"""
Constants for AI model providers and application configuration.
"""

# Gemini Model Constants
class GeminiConstants:
    """Constants for Google Gemini AI model configuration."""
    
    # Default generation parameters
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_OUTPUT_TOKENS = 4096
    DEFAULT_TOP_P = 0.9
    DEFAULT_TOP_K = 40
    
    # Token limits and constraints
    MAX_PROMPT_TOKENS = 1500
    MIN_OUTPUT_TOKENS = 1
    MAX_OUTPUT_TOKENS_LIMIT = 8192
    
    # Model versions
    DEFAULT_MODEL = "gemini-pro"
    FLASH_MODEL = "gemini-2.0-flash-exp"
    PRO_MODEL = "gemini-pro"


# OpenAI Model Constants
class OpenAIConstants:
    """Constants for OpenAI model configuration."""
    
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 4096
    DEFAULT_TOP_P = 1.0
    DEFAULT_FREQUENCY_PENALTY = 0.0
    DEFAULT_PRESENCE_PENALTY = 0.0
    
    DEFAULT_MODEL = "gpt-4"


# Anthropic Model Constants  
class AnthropicConstants:
    """Constants for Anthropic Claude model configuration."""
    
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 4096
    DEFAULT_TOP_P = 1.0
    DEFAULT_TOP_K = 5
    
    DEFAULT_MODEL = "claude-3-sonnet-20240229"


# General AI Constants
class AIConstants:
    """General constants for AI processing."""
    
    # Token estimation (approximate ratios)
    TOKENS_PER_WORD_GEMINI = 1.3
    TOKENS_PER_WORD_OPENAI = 1.2
    TOKENS_PER_WORD_ANTHROPIC = 1.2
    
    # Response limits
    MIN_RESPONSE_LENGTH = 10
    MAX_RESPONSE_LENGTH = 32000
    
    # Timeout settings
    API_TIMEOUT_SECONDS = 60
    HEALTH_CHECK_TIMEOUT = 10


# Slack Bot Constants
class SlackConstants:
    """Constants for Slack bot configuration."""
    
    # Message limits
    MAX_MESSAGE_LENGTH = 4000
    MAX_THREAD_DEPTH = 50
    
    # Retry settings
    MAX_RETRIES = 3
    RETRY_DELAY_SECONDS = 1
    
    # Bot behavior
    TYPING_INDICATOR_DELAY = 0.5
    CONTEXT_WINDOW_MESSAGES = 20


# Error Messages
class ErrorMessages:
    """Standard error messages for the application."""
    
    EMPTY_RESPONSE = "Received empty response from AI model"
    TOKEN_LIMIT_EXCEEDED = "Response truncated due to token limit"
    API_KEY_MISSING = "API key is required but not provided"
    MODEL_INITIALIZATION_FAILED = "Failed to initialize AI model"
    SLACK_CONNECTION_FAILED = "Failed to connect to Slack"
    INVALID_CONFIGURATION = "Invalid configuration provided"
