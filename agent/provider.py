import os
import sys
from typing import Dict, List, Any, AnyStr
from openai import OpenAI, APIConnectionError, APIStatusError
from dotenv import load_dotenv
from .config import AGENT_NAME
import logging

logging.basicConfig(
    level=logging.WARNING,  # Отсекаем лишний шум от httpx и openai (уровень INFO/DEBUG)
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("llm_client")

load_dotenv()

api_key = f"{os.getenv("AGENT_API")}"
BASE_URL = f"{os.getenv("BASE_URL")}"
if not api_key or not api_key.strip():
    raise ValueError("Ошибка конфигурации: не задана переменная окружения OPENAI_API_KEY.")

client = OpenAI(
    api_key=api_key,
    base_url=BASE_URL 
)

def chat_completion(question: str, show_metadata: bool = True):
    try:
        response = client.chat.completions.create(
        model=AGENT_NAME,  
        messages=[
            {"role": "system", "content": "Ты полезный ассистент."},
            {"role": "user", "content": f"{question}"}
            ]
        )

        if show_metadata:
            print(f"\n[Tokens: {response.usage.total_tokens} | Model: {response.model}")

        return response.choices[0].message.content

    except ValueError as e:
        # Выводим понятное сообщение об отсутствии ключа без страшного traceback
        logger.error(str(e))
        sys.exit(1)

    except APIConnectionError:
        # Ошибка сети или неверный base_url (не выводим детали сокета/прокси с кредами)
        logger.error("Не удалось подключиться к серверу API. Проверьте интернет или base_url.")
        sys.exit(1)

    except APIStatusError as e:
        # 2. Безопасная обработка HTTP-ошибок (401, 429, 500 и т.д.)
        # Логируем только код статуса и сообщение сервера, не трогая заголовки запроса (e.request.headers)
        logger.error(f"HTTP ошибка от провайдера (код {e.status_code}): {e.message}")
        sys.exit(1)