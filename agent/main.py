import argparse
import logging
import sys

from dotenv import load_dotenv

from . import provider
from .agent import Agent
from .config import AGENT_NAME, MAX_MESSAGES
from .provider import ProviderError


logger = logging.getLogger("agent.main")


def build_agent() -> Agent:
    return Agent(
        provider=provider,
        model=AGENT_NAME,
        max_history_messages=MAX_MESSAGES,
    )


def run_prompt(agent: Agent, prompt: str) -> None:
    try:
        response = agent.send(prompt)
        print(f"Response: {response}")
    except ProviderError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def run_chat(agent: Agent) -> None:
    print("Type /exit to quit, /reset to clear, /history to show memory.\n")

    while True:
        try:
            user_text = input("You: ").strip()
        except EOFError:
            print("\nBye.")
            break
        except KeyboardInterrupt:
            print("\nBye.")
            break

        if not user_text:
            continue

        if user_text in ("/exit", "/quit"):
            print("Bye.")
            break

        if user_text == "/reset":
            agent.reset()
            print("[history cleared]")
            continue

        if user_text == "/history":
            for message in agent.history():
                print(f"{message['role']}: {message['content']}")
            continue

        try:
            reply = agent.send(user_text)
            print(f"Agent: {reply}\n")
        except ProviderError as exc:
            print(f"Error: {exc}\n", file=sys.stderr)


def main() -> None:
    load_dotenv()

    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s [%(levelname)s] %(message)s",
        stream=sys.stderr,
    )

    parser = argparse.ArgumentParser(description="Budget ML Agent CLI")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prompt", type=str, help="Single prompt")
    group.add_argument("--chat", action="store_true", help="Interactive chat mode")

    args = parser.parse_args()

    agent = build_agent()

    if args.prompt is not None:
        run_prompt(agent, args.prompt)
    elif args.chat:
        run_chat(agent)


if __name__ == "__main__":
    main()