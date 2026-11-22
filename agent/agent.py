from typing import Optional, Protocol


class ChatProvider(Protocol):
    def chat_completion(self, messages: list[dict], model: str) -> str:
        ...


DEFAULT_SYSTEM_PROMPT = (
    "You are a concise, helpful assistant. "
    "Answer briefly and stay on topic."
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

    def _trimmed_history(self) -> list[dict]:
        if self.max_history_messages == 0:
            return []
        return self.messages[-self.max_history_messages:]

    def _payload_messages(self) -> list[dict]:
        return [
            {"role": "system", "content": self.system_prompt}
        ] + self._trimmed_history()

    def send(self, user_text: str) -> str:
        user_message = {"role": "user", "content": user_text}
        self.messages.append(user_message)

        try:
            assistant_text = self.provider.chat_completion(
                messages=self._payload_messages(),
                model=self.model,
            )
        except Exception:
            self.messages.pop()
            raise

        if not isinstance(assistant_text, str) or not assistant_text.strip():
            self.messages.pop()
            raise RuntimeError("Provider returned empty response")

        self.messages.append({"role": "assistant", "content": assistant_text})
        return assistant_text

    def reset(self) -> None:
        self.messages.clear()

    def history(self) -> list[dict]:
        return [dict(message) for message in self.messages]