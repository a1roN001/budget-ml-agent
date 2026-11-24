import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = PROJECT_ROOT / "logs"
USAGE_LOG_FILE = LOGS_DIR / "usage.jsonl"

INPUT_PRICE_PER_1M = float(os.getenv("INPUT_PRICE_PER_1M_TOKENS", "0.15"))
OUTPUT_PRICE_PER_1M = float(os.getenv("OUTPUT_PRICE_PER_1M_TOKENS", "0.60"))

AGENT_NAME = "deepseek-v4.1-flash-1017"
MAX_MESSAGES = 5

SHOW_METADATA = False

