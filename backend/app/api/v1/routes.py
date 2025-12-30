import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse, JSONResponse

from app.core.openai_client import OpenAIClient
from app.core.token_tracker import TokenTracker
from app.models.requests import AIRequest
from app.models.responses import AIResponse, UsageRecentResponse, ErrorResponse
from app.core.errors import map_exception

router = APIRouter()

client = OpenAIClient()
tracker = TokenTracker()


def get_client():
    return client


def get_tracker():
    return tracker


@router.post("/ai", response_model=AIResponse)
async def ai(req: AIRequest, client: OpenAIClient = Depends(get_client), tracker: TokenTracker = Depends(get_tracker)):
    try:
        result = await client.generate_completion(req)
        cost = tracker.record(id=result.id, task=result.task, model=result.model, usage=result.usage.model_dump())
        result.usage.estimated_cost = cost
        return result
    except Exception as exc:  # noqa: BLE001
        raise map_exception(exc)


@router.post("/ai/stream")
async def ai_stream(req: AIRequest, client: OpenAIClient = Depends(get_client), tracker: TokenTracker = Depends(get_tracker)):
    async def event_stream():
        try:
            async for evt in client.stream_completion(req):
                if evt["type"] == "chunk":
                    payload = json.dumps({"text": evt["data"]})
                    yield f"event: chunk\ndata: {payload}\n\n"
                elif evt["type"] == "end":
                    usage = evt.get("usage", {})
                    cost = tracker.record(
                        id=evt.get("id", ""),
                        task=req.task,
                        model=evt.get("model", ""),
                        usage=usage,
                    )
                    end_payload = {
                        "usage": usage,
                        "model": evt.get("model"),
                        "task": req.task,
                        "estimated_cost": cost,
                        "id": evt.get("id", ""),
                    }
                    yield f"event: end\ndata: {json.dumps(end_payload)}\n\n"
                elif evt["type"] == "error":
                    yield f"event: error\ndata: {json.dumps({'message': evt['message']})}\n\n"
        except Exception as exc:  # noqa: BLE001
            http_exc = map_exception(exc)
            detail = http_exc.detail
            if isinstance(detail, dict):
                payload = json.dumps(detail)
            else:
                payload = json.dumps({"message": str(detail)})
            yield f"event: error\ndata: {payload}\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/usage/recent", response_model=UsageRecentResponse)
async def usage_recent(tracker: TokenTracker = Depends(get_tracker)):
    return {"items": tracker.get_recent()}
