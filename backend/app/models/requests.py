from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field, validator


class AIRequest(BaseModel):
    task: Literal["summarize", "translate", "generate"] = Field(
        ..., description="Type of AI operation"
    )
    input_text: str = Field(..., min_length=1, description="User-provided text")
    target_language: Optional[str] = Field(
        None, description="Required when task is 'translate'"
    )
    options: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional model settings like temperature, max_tokens, etc.",
    )

    @validator("target_language")
    def validate_target_language(cls, v, values):  # noqa: N805
        if values.get("task") == "translate" and not v:
            raise ValueError("target_language is required for translate")
        return v
