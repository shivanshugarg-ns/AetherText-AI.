import os
from enum import Enum
from typing import AsyncGenerator, Dict, Tuple

from openai import AsyncOpenAI
from pydantic import BaseModel


class PromptConfig(str, Enum):
    summarize = "summarize"
    translate = "translate"
    generate = "generate"


class GenerateRequest(BaseModel):
    mode: PromptConfig
    content: str
    target_language: str | None = None
    stream: bool = False


class OpenAIService:
    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = AsyncOpenAI(api_key=api_key) if api_key else None
        self.default_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def _build_messages(self, req: GenerateRequest):
        system = "You are a concise assistant that writes clear, direct responses."
        if req.mode == PromptConfig.summarize:
            user = f"Summarize the following text:\n\n{req.content}"
        elif req.mode == PromptConfig.translate:
            target = req.target_language or "English"
            user = f"Translate the following text to {target}:\n\n{req.content}"
        else:
            user = f"Generate engaging content based on the following request:\n\n{req.content}"
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

    async def generate(self, req: GenerateRequest) -> Tuple[str, Dict]:
        if not self.client:
            raise RuntimeError("OPENAI_API_KEY missing")

        messages = self._build_messages(req)

        response = await self.client.chat.completions.create(
            model=self.default_model,
            messages=messages,
            temperature=0.6 if req.mode != PromptConfig.translate else 0.3,
            max_tokens=600,
        )

        content = response.choices[0].message.content or ""
        usage = response.usage.model_dump() if response.usage else {}
        usage["model"] = response.model
        return content.strip(), usage

    async def stream_generate(
        self, req: GenerateRequest
    ) -> AsyncGenerator[Dict[str, str | Dict], None]:
        """
        Yields dict events:
          {"type": "chunk", "data": <text delta>}
          {"type": "usage", "data": <usage dict>}  # only once, at end when provided
        """
        if not self.client:
            raise RuntimeError("OPENAI_API_KEY missing")

        messages = self._build_messages(req)

        stream = await self.client.chat.completions.create(
            model=self.default_model,
            messages=messages,
            temperature=0.6 if req.mode != PromptConfig.translate else 0.3,
            max_tokens=600,
            stream=True,
        )

        async for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                yield {"type": "chunk", "data": delta}
            if chunk.usage:
                usage = chunk.usage.model_dump()
                usage["model"] = chunk.model
                yield {"type": "usage", "data": usage}
