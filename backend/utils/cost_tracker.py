from dataclasses import dataclass, field
from typing import Dict

# Simplified per-1k token costs; adjust as needed for chosen model
MODEL_PRICING = {
    "gpt-4o-mini": {"prompt": 0.00015, "completion": 0.00060},
    "gpt-4o": {"prompt": 0.005, "completion": 0.015},
}


@dataclass
class UsageRecord:
    prompt_tokens: int
    completion_tokens: int
    model: str
    cost: float = field(init=False)

    def __post_init__(self):
        pricing = MODEL_PRICING.get(self.model, MODEL_PRICING["gpt-4o-mini"])
        self.cost = (
            (self.prompt_tokens / 1000) * pricing["prompt"]
            + (self.completion_tokens / 1000) * pricing["completion"]
        )

    def to_dict(self) -> Dict[str, int | str | float]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "model": self.model,
        }


class CostTracker:
    def __init__(self) -> None:
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost = 0.0

    def add_record(self, record: UsageRecord):
        self.total_prompt_tokens += record.prompt_tokens
        self.total_completion_tokens += record.completion_tokens
        self.total_cost += record.cost
        return self.summary()

    def summary(self):
        return {
            "prompt_tokens": self.total_prompt_tokens,
            "completion_tokens": self.total_completion_tokens,
            "cost_usd": round(self.total_cost, 6),
        }
