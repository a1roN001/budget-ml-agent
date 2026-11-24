import time
from datetime import datetime, timezone
from typing import Optional, Protocol
from .usage import UsageRecord, SessionTracker, calculate_cost, log_usage

from .provider import chat_completion
import os
from typing import Optional

from dotenv import load_dotenv
from openai import APIConnectionError, APIStatusError, OpenAI


class ProviderError(RuntimeError):
    pass


_client: Optional[OpenAI] = None


def _get_client() -> OpenAI:
    global _client

    if _client is None:
        load_dotenv()

        api_key = os.getenv("AGENT_API")
        base_url = os.getenv("BASE_URL")

        if not api_key or not api_key.strip():
            raise ProviderError("AGENT_API environment variable is not set")

        if not base_url or not base_url.strip():
            raise ProviderError("BASE_URL environment variable is not set")

        _client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

    return _client

class ChatProvider(Protocol):
    def chat_completion(self, messages: list[dict], model: str) -> str:
        client = _get_client()

        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
            )
        except APIConnectionError as exc:
            raise ProviderError("Failed to connect to provider") from exc
        except APIStatusError as exc:
            raise ProviderError(
                f"Provider returned HTTP error {exc.status_code}"
            ) from exc

        if not response.choices:
            raise ProviderError("Provider returned no choices")

        content = response.choices[0].message.content

        if not content or not content.strip():
            raise ProviderError("Provider returned empty response content")

        return response


DEFAULT_SYSTEM_PROMPT = (
    "You are a concise, helpful assistant. "
    "Answer briefly and stay on topic."
    "Don's answer with markdown, use regular text"
)


class Agent:
    """Minimal in-memory conversational agent."""

    def __init__(
        self,
        provider: ChatProvider,
        model: str,
        max_history_messages: int,
        system_prompt: Optional[str] = None,
    ):
        if max_history_messages < 0:
            raise ValueError("max_history_messages must be non-negative")

        self.provider = provider
        self.model = model
        self.max_history_messages = max_history_messages
        self.system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT
        self.messages: list[dict] = []
        self.tracker = SessionTracker()


    def _trimmed_history(self) -> list[dict]:
        if self.max_history_messages == 0:
            return []
        return self.messages[-self.max_history_messages:]

    def _payload_messages(self) -> list[dict]:
        return [
            {"role": "system", "content": self.system_prompt}
        ] + self._trimmed_history()

    def send(self, user_text: str) -> str:
        start_time = time.time()

        user_message = {"role": "user", "content": user_text}
        self.messages.append(user_message)

        try:
            response_obj = self.provider.chat_completion( 
                messages=self._payload_messages(),
                model=self.model,
            )
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            # Extract usage safely
            p_tokens = getattr(response_obj.usage, 'prompt_tokens', 0) or 0
            c_tokens = getattr(response_obj.usage, 'completion_tokens', 0) or 0
            t_tokens = getattr(response_obj.usage, 'total_tokens', 0) or 0
            
            cost = calculate_cost(p_tokens, c_tokens)
            
            record = UsageRecord(
                timestamp=datetime.now(timezone.utc).isoformat(),
                model=self.model,
                prompt_tokens=p_tokens,
                completion_tokens=c_tokens,
                total_tokens=t_tokens,
                estimated_cost_usd=cost,
                latency_ms=round(latency_ms, 2)
            )
            
            # 1. Persist to disk
            log_usage(record)
            
            # 2. Accumulate in memory
            self.tracker.add_record(record)
            
            # ... append assistant message ...
            return response_obj.choices[0].message.content
        
        except Exception:
            self.messages.pop()
            raise

    def reset(self) -> None:
        self.messages.clear()

    def history(self) -> list[dict]:
        return [dict(message) for message in self.messages]