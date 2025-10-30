from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Union
from enum import Enum
from datetime import datetime
import time

class ModelTypeDTO(str, Enum):
    USER = "user"
    SYSTEM = "system"
    ASSISTANT = "assistant"

class MessageDTO(BaseModel):
    role: ModelTypeDTO
    content: str
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)

class ChatRequestDTO(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="User's question or message")
    max_tokens: Optional[int] = Field(default=200, ge=1, le=1000, description="Maximum tokens to generate")

    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()

class ChatResponseDTO(BaseModel):
    response: str
    timestamp: float = Field(default_factory=lambda: time.time())
    response_time: Optional[float] = None
    model_used: str = "custom-llama"

class HealthResponseDTO(BaseModel):
    status: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    model_loaded: bool
    memory_usage: Optional[str] = None


class StreamChatRequestDTO(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="User's current message")
    max_tokens: Optional[int] = Field(default=500, ge=1, le=1000, description="Maximum tokens to generate")

    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()

class ErrorResponseDTO(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)



