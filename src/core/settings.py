import os

from pathlib import Path
from environs import Env

env = Env()
env.read_env()

BOT_TOKEN: str = env.str("BOT_TOKEN")
REDIS_URL: str = env.str("REDIS_URL", default="redis://localhost:5432/0")

BASE_DIR = Path(__file__).resolve().parent.parent.parent

TEMP_DIR = BASE_DIR / "temp"

os.makedirs(TEMP_DIR, exist_ok=True)
