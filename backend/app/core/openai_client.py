import logging
import uuid
from typing import AsyncGenerator, Dict

from openai import AsyncOpenAI

from app.core.config import settings
from app.core.errors import OpenAIFallbackError
from app.models.requests import AIRequest
from app.models.responses import AIResponse, TokenUsage

logger = logging.getLogger(__name__)


class OpenAIClient:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.default_model = settings.openai_default_model
        self.fallback_model = settings.openai_fallback_model

    def _prompt_for(self, req: AIRequest) -> str:
        if req.task == "summarize":
            return f"Summarize the following text in a clear and concise way:\n\n{req.input_text}"
        if req.task == "translate":
            target = req.target_language or "English"
            return f"Translate the following text into {target}:\n\n{req.input_text}"
        # generate
        genre = None
        if req.options:
            genre = req.options.get("genre")
        descriptor = genre or "content"
        return f"Generate a {descriptor} based on this instruction:\n\n{req.input_text}"

    async def _call_chat(self, req: AIRequest, model: str, stream: bool = False):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": self._prompt_for(req)},
        ]
        kwargs: Dict = {
            "model": model,
            "messages": messages,
            "temperature": req.options.get("temperature", 0.6) if req.options else 0.6,
            "max_tokens": req.options.get("max_tokens", 600) if req.options else 600,
            "stream": stream,
        }
        return await self.client.chat.completions.create(**kwargs)

    async def generate_completion(self, req: AIRequest) -> AIResponse:
        request_id = str(uuid.uuid4())
        try:
            response = await self._call_chat(req, self.default_model, stream=False)
        except Exception as primary_exc:  # noqa: BLE001
            logger.warning("Primary model failed; attempting fallback", exc_info=primary_exc)
            try:
                response = await self._call_chat(req, self.fallback_model, stream=False)
            except Exception as fallback_exc:  # noqa: BLE001
                logger.error("Fallback model failed", exc_info=fallback_exc)
                raise OpenAIFallbackError()

        choice = response.choices[0].message
        usage = response.usage.model_dump() if response.usage else {}
        usage.setdefault("prompt_tokens", 0)
        usage.setdefault("completion_tokens", 0)
        usage.setdefault("total_tokens", usage.get("prompt_tokens", 0) + usage.get("completion_tokens", 0))
        return AIResponse(
            id=request_id,
            task=req.task,
            model=response.model,
            input_text=req.input_text,
            output_text=choice.content or "",
            usage=TokenUsage(**usage, estimated_cost=0.0),
            created_at=response.created or "",
        )

    async def stream_completion(
        self, req: AIRequest
    ) -> AsyncGenerator[Dict[str, object], None]:
        request_id = str(uuid.uuid4())
        model_used = self.default_model
        stream = None
        try:
            stream = await self._call_chat(req, self.default_model, stream=True)
        except Exception as primary_exc:  # noqa: BLE001
            logger.warning("Primary model failed; attempting fallback stream", exc_info=primary_exc)
            try:
                model_used = self.fallback_model
                stream = await self._call_chat(req, self.fallback_model, stream=True)
            except Exception as fallback_exc:  # noqa: BLE001
                logger.error("Fallback stream failed", exc_info=fallback_exc)
                raise OpenAIFallbackError()

        collected_text = ""
        usage = {}
        async for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                collected_text += delta
                yield {"type": "chunk", "data": delta}
            if chunk.usage:
                usage = chunk.usage.model_dump()

        usage.setdefault("prompt_tokens", 0)
        usage.setdefault("completion_tokens", 0)
        usage.setdefault("total_tokens", usage.get("prompt_tokens", 0) + usage.get("completion_tokens", 0))

        yield {
            "type": "end",
            "id": request_id,
            "usage": usage,
            "model": model_used,
            "output": collected_text,
        }
