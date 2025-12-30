import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_default_model: str = Field("gpt-4.1-mini", env="OPENAI_DEFAULT_MODEL")
    openai_fallback_model: str = Field("gpt-4o-mini", env="OPENAI_FALLBACK_MODEL")
    prompt_cost_per_1k: float = Field(0.15, env="OPENAI_PROMPT_COST_PER_1K")
    completion_cost_per_1k: float = Field(0.60, env="OPENAI_COMPLETION_COST_PER_1K")
    backend_port: int = Field(8000, env="BACKEND_PORT")
    backend_host: str = Field("0.0.0.0", env="BACKEND_HOST")
    frontend_origin: str = Field("http://localhost:5173", env="FRONTEND_ORIGIN")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
