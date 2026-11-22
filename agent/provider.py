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


def chat_completion(messages: list[dict], model: str) -> str:
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

    return content