from typing import List, Dict, Any, Optional
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
from ..models.base import AIModelInterface, AIMessage, AIResponse
import logging

logger = logging.getLogger(__name__)


class LocalHuggingFaceModel(AIModelInterface):
    """Local HuggingFace model implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._model_path = config.get("model_path", "microsoft/DialoGPT-medium")
        self._model_name = config.get("model_name", self._model_path)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Initialize model and tokenizer
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self._model_path)
            self.model = AutoModelForCausalLM.from_pretrained(
                self._model_path,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None
            )
            
            # Set pad token if not exists
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1
            )
            
        except Exception as e:
            logger.error(f"Failed to load local model: {str(e)}")
            raise
    
    async def generate_response(
        self, 
        messages: List[AIMessage], 
        **kwargs
    ) -> AIResponse:
        """Generate response using local HuggingFace model."""
        try:
            # Convert messages to a single prompt
            prompt = self._format_messages(messages)
            
            # Generate response
            max_tokens = kwargs.get("max_tokens", 100)
            temperature = kwargs.get("temperature", 0.7)
            
            result = self.pipeline(
                prompt,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                truncation=True,
                return_full_text=False
            )
            
            generated_text = result[0]["generated_text"]
            
            return AIResponse(
                content=generated_text.strip(),
                model=self._model_name,
                usage={
                    "prompt_tokens": len(self.tokenizer.encode(prompt)),
                    "completion_tokens": len(self.tokenizer.encode(generated_text)),
                    "total_tokens": len(self.tokenizer.encode(prompt + generated_text))
                },
                metadata={"device": self.device}
            )
            
        except Exception as e:
            logger.error(f"Local model generation error: {str(e)}")
            raise
    
    def _format_messages(self, messages: List[AIMessage]) -> str:
        """Format messages into a single prompt."""
        formatted_parts = []
        
        for msg in messages:
            if msg.role == "system":
                formatted_parts.append(f"System: {msg.content}")
            elif msg.role == "user":
                formatted_parts.append(f"Human: {msg.content}")
            elif msg.role == "assistant":
                formatted_parts.append(f"Assistant: {msg.content}")
        
        formatted_parts.append("Assistant:")
        return "\n".join(formatted_parts)
    
    async def health_check(self) -> bool:
        """Check if local model is available."""
        try:
            test_messages = [AIMessage(role="user", content="Hello")]
            response = await self.generate_response(test_messages, max_tokens=1)
            return len(response.content) > 0
        except Exception as e:
            logger.error(f"Local model health check failed: {str(e)}")
            return False
    
    @property
    def model_name(self) -> str:
        return self._model_name
    
    @property
    def provider(self) -> str:
        return "local"
