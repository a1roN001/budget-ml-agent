import json
import time
from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime, timezone

from .config import USAGE_LOG_FILE, INPUT_PRICE_PER_1M, OUTPUT_PRICE_PER_1M


@dataclass
class UsageRecord:
    timestamp: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_usd: Optional[float]
    latency_ms: float

    def to_json_line(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False) + "\n"


class SessionTracker:
    """Accumulates usage stats in memory for the current session."""
    
    def __init__(self):
        self.requests_count = 0
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost_usd = 0.0
        self.total_latency_ms = 0.0

    def add_record(self, record: UsageRecord):
        self.requests_count += 1
        self.total_prompt_tokens += record.prompt_tokens
        self.total_completion_tokens += record.completion_tokens
        
        if record.estimated_cost_usd is not None:
            self.total_cost_usd += record.estimated_cost_usd
            
        self.total_latency_ms += record.latency_ms

    def get_summary_text(self) -> str:
        avg_latency = self.total_latency_ms / self.requests_count if self.requests_count > 0 else 0
        return (
            f"Session Statistics:\n"
            f"Requests: {self.requests_count}\n"
            f"Input Tokens: {self.total_prompt_tokens:,}\n"
            f"Output Tokens: {self.total_completion_tokens:,}\n"
            f"Total Cost: ${self.total_cost_usd:.6f}\n"
            f"Avg Latency: {avg_latency:.1f} ms"
        )


def calculate_cost(prompt_tokens: int, completion_tokens: int) -> Optional[float]:
    """Calculates cost based on configured prices. Returns None if inputs are invalid."""
    if prompt_tokens < 0 or completion_tokens < 0:
        return None
    
    cost_input = (prompt_tokens / 1_000_000) * INPUT_PRICE_PER_1M
    cost_output = (completion_tokens / 1_000_000) * OUTPUT_PRICE_PER_1M
    return round(cost_input + cost_output, 8)


def log_usage(record: UsageRecord):
    """Appends a single JSON line to the persistent log file."""
    try:
        USAGE_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with open(USAGE_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(record.to_json_line())
    except IOError as e:
        print(f"Warning: Could not write to usage log: {e}")