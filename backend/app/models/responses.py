from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost: float = 0.0


class AIResponse(BaseModel):
    id: str
    task: str
    model: str
    input_text: str
    output_text: str
    usage: TokenUsage
    created_at: str


class ErrorInfo(BaseModel):
    type: str
    message: str
    detail: Optional[str] = None
    retryable: bool = False


class ErrorResponse(BaseModel):
    error: ErrorInfo


class UsageHistoryItem(BaseModel):
    id: str
    task: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost: float
    created_at: str


class UsageRecentResponse(BaseModel):
    items: List[UsageHistoryItem]
