from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List

from app.core.config import settings


@dataclass
class UsageRecord:
    id: str
    task: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost: float
    created_at: str


class TokenTracker:
    def __init__(self, max_history: int = 50) -> None:
        self.history: List[UsageRecord] = []
        self.max_history = max_history

    def _estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        cost = (
            (prompt_tokens / 1000) * settings.prompt_cost_per_1k
            + (completion_tokens / 1000) * settings.completion_cost_per_1k
        )
        return round(cost, 6)

    def record(self, *, id: str, task: str, model: str, usage: dict) -> float:
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)
        cost = self._estimate_cost(prompt_tokens, completion_tokens)
        record = UsageRecord(
            id=id,
            task=task,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            estimated_cost=cost,
            created_at=datetime.utcnow().isoformat(),
        )
        self.history.append(record)
        if len(self.history) > self.max_history:
            self.history.pop(0)
        return cost

    def get_recent(self, limit: int = 20) -> list[dict]:
        items = self.history[-limit:]
        return [record.__dict__ for record in items]
