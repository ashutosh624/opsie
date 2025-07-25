from typing import List, Dict, Any
import anthropic
from ..models.base import AIModelInterface, AIMessage, AIResponse
import logging

logger = logging.getLogger(__name__)


class AnthropicModel(AIModelInterface):
    """Anthropic model implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = anthropic.AsyncAnthropic(
            api_key=config.get("api_key")
        )
        self._model_name = config.get("model", "claude-3-sonnet-20240229")
    
    async def generate_response(
        self, 
        messages: List[AIMessage], 
        **kwargs
    ) -> AIResponse:
        """Generate response using Anthropic API."""
        try:
            # Convert AIMessage to Anthropic format
            anthropic_messages = []
            system_message = None
            
            for msg in messages:
                if msg.role == "system":
                    system_message = msg.content
                else:
                    anthropic_messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
            
            create_params = {
                "model": self._model_name,
                "messages": anthropic_messages,
                "max_tokens": kwargs.get("max_tokens", 1000),
                "temperature": kwargs.get("temperature", 0.7),
            }
            
            if system_message:
                create_params["system"] = system_message
                
            response = await self.client.messages.create(**create_params)
            
            usage = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            } if response.usage else None
            
            return AIResponse(
                content=response.content[0].text,
                model=response.model,
                usage=usage,
                metadata={"stop_reason": response.stop_reason}
            )
            
        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise
    
    async def health_check(self) -> bool:
        """Check Anthropic API health."""
        try:
            response = await self.client.messages.create(
                model=self._model_name,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=1
            )
            return True
        except Exception as e:
            logger.error(f"Anthropic health check failed: {str(e)}")
            return False
    
    @property
    def model_name(self) -> str:
        return self._model_name
    
    @property
    def provider(self) -> str:
        return "anthropic"
