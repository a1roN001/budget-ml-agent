import argparse
import sys
from .provider import chat_completion
import logging
from openai import OpenAI

logging.basicConfig(
    level=logging.WARNING,  # Отсекаем лишний шум от httpx и openai (уровень INFO/DEBUG)
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("llm_client")

def run_agent(prompt: str):
    print(f"Агент получил задачу: {prompt}")
    print(f"Responce:{chat_completion(question=prompt)}")

def main():
    parser = argparse.ArgumentParser(description="CLI для запуска агента")
    parser.add_argument("--prompt", type=str, help="Запрос или команда для агента")
    
    args = parser.parse_args()
    run_agent(args.prompt)

if __name__ == "__main__":
    main()
