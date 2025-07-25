from typing import List, Dict, Any
import openai
from ..models.base import AIModelInterface, AIMessage, AIResponse
import logging

logger = logging.getLogger(__name__)


class OpenAIModel(AIModelInterface):
    """OpenAI model implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = openai.AsyncOpenAI(
            api_key=config.get("api_key")
        )
        self._model_name = config.get("model", "gpt-4")
    
    async def generate_response(
        self, 
        messages: List[AIMessage], 
        **kwargs
    ) -> AIResponse:
        """Generate response using OpenAI API."""
        try:
            # Convert AIMessage to OpenAI format
            openai_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            response = await self.client.chat.completions.create(
                model=self._model_name,
                messages=openai_messages,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 1000),
                **{k: v for k, v in kwargs.items() 
                   if k in ["top_p", "frequency_penalty", "presence_penalty"]}
            )
            
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            } if response.usage else None
            
            return AIResponse(
                content=response.choices[0].message.content,
                model=response.model,
                usage=usage,
                metadata={"finish_reason": response.choices[0].finish_reason}
            )
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    async def health_check(self) -> bool:
        """Check OpenAI API health."""
        try:
            response = await self.client.chat.completions.create(
                model=self._model_name,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=1
            )
            return True
        except Exception as e:
            logger.error(f"OpenAI health check failed: {str(e)}")
            return False
    
    @property
    def model_name(self) -> str:
        return self._model_name
    
    @property
    def provider(self) -> str:
        return "openai"
