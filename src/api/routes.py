from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from ..agent.ai_agent import AIAgent
from ..config import config

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Agent Slack Bot API",
    description="REST API for the AI Agent Slack Bot",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI agent
ai_agent = AIAgent()


# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str
    user_id: str
    provider: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000


class ChatResponse(BaseModel):
    response: str
    provider: str
    model: str


class HealthResponse(BaseModel):
    status: str
    message: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None


# API Routes
@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "AI Agent Slack Bot API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        health_status = await ai_agent.health_check()
        return HealthResponse(**health_status)
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint for direct AI interaction."""
    try:
        response = await ai_agent.process_message(
            user_id=request.user_id,
            message=request.message,
            provider=request.provider,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        model_info = ai_agent.get_current_model_info()
        
        return ChatResponse(
            response=response,
            provider=model_info["provider"],
            model=model_info["model"]
        )
    
    except Exception as e:
        logger.error(f"Chat request failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models")
async def get_models():
    """Get available AI models."""
    try:
        available_providers = ai_agent.get_available_providers()
        current_model = ai_agent.get_current_model_info()
        
        return {
            "available_providers": available_providers,
            "current_provider": current_model["provider"],
            "current_model": current_model["model"]
        }
    
    except Exception as e:
        logger.error(f"Failed to get models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/models/switch/{provider}")
async def switch_model(provider: str):
    """Switch to a different AI model provider."""
    try:
        available_providers = ai_agent.get_available_providers()
        
        if provider not in available_providers:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown provider: {provider}. Available: {available_providers}"
            )
        
        # Switch model by processing a dummy message
        await ai_agent.process_message("system", "ping", provider=provider)
        model_info = ai_agent.get_current_model_info()
        
        return {
            "message": f"Switched to {provider}",
            "provider": model_info["provider"],
            "model": model_info["model"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to switch model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/conversations/{user_id}")
async def clear_conversation(user_id: str):
    """Clear conversation history for a user."""
    try:
        await ai_agent.clear_conversation(user_id)
        return {"message": f"Conversation history cleared for user {user_id}"}
    
    except Exception as e:
        logger.error(f"Failed to clear conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
