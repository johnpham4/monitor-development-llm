from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse, StreamingResponse
from loguru import logger
import time
import json
from typing import Optional, Generator

# Import models và services
from .dto import ChatRequestDTO, ChatResponseDTO, ErrorResponseDTO, StreamChatRequestDTO
from .chat_service import chatService

# Tạo router
router = APIRouter()

@router.post("/generate", response_model=ChatResponseDTO, status_code=status.HTTP_200_OK)
async def generate_chat_response(request: ChatRequestDTO):
    """
    Generate AI response for user message
    """

    # start timer for response time measurement
    start_time = time.time()

    # Generate response using the service
    try:
        ai_response = chatService.generate_response(
            user_input=request.message,
            max_tokens=request.max_tokens,
        )

    except Exception as e:
        logger.error(f"Error generating AI response: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate response. Please try again."
        )

    response_time = time.time() - start_time

    # Return response (không save database)
    return ChatResponseDTO(
        response=ai_response,
        response_time=response_time,
        model_used="gguf",
        timestamp=time.time()
    )

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_usage_mb = memory_info.rss / 1024 / 1024

        return {
            "status": "healthy",
            "service": "chat-service",
            "version": "1.0.0",
            "model_loaded": chatService.is_model_loaded(),
            "memory_usage_mb": round(memory_usage_mb, 2),
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
        }

@router.get("/model/status")
async def get_model_status():
    """
    Get model status and information
    """
    try:
        return {
            "model_loaded": chatService.is_model_loaded(),
            "model_path": chatService.model_path,
            "device": chatService.device if hasattr(chatService, 'device') else "unknown",
        }
    except Exception as e:
        logger.error(f"Error getting model status: {e}")
        return {
            "error": str(e),
            "timestamp": time.time()
        }

@router.post("/chat/stream")
async def stream_chat_response(request: StreamChatRequestDTO):
    """
    Stream AI response for chat interface
    """
    try:
        # Validate model is loaded
        if not chatService.is_model_loaded():
            logger.warning("Model not loaded, attempting to load...")
            try:
                await chatService.load_model()
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="AI model is not available. Please try again later."
                )

        # Create streaming generator
        def generate_stream():
            try:
                # Build context như notebook - chỉ dùng current message
                user_message = request.message

                # Use real streaming từ ChatService (như notebook)
                for content_chunk in chatService.streaming_response(
                    user_input=user_message,
                    max_tokens=request.max_tokens or 256,
                ):
                    if content_chunk:  # Only send non-empty chunks
                        data = {
                            "content": content_chunk,
                            "type": "chunk"
                        }
                        yield f"data: {json.dumps(data)}\n\n"

                # Send completion signal
                yield f"data: [DONE]\n\n"

            except Exception as e:
                logger.error(f"Error in stream generation: {e}")
                error_data = {
                    "error": str(e),
                    "type": "error"
                }
                yield f"data: {json.dumps(error_data)}\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/plain; charset=utf-8"
            }
        )

    except Exception as e:
        logger.error(f"Error in stream chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat request"
        )

# Export router
Router = router

