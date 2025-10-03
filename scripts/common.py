import time
import random
import urllib.parse
import logging
from typing import Dict, Any

def jitter_sleep(base_min: float = 0.8, base_max: float = 1.6):
    time.sleep(random.uniform(base_min, base_max))

def build_ua() -> str:
    return "MMA-BOT-WaybackHarvester/1.0 (+https://github.com/brawlandorder/ufc-master-index)"

def sanitize_path(url: str) -> str:
    # Make filesystem-safe path fragments
    safe = url.replace("://", "_").replace("/", "_").replace("?", "_").replace("&", "_").replace("=", "-")
    return safe

def setup_logging(level: str = "INFO"):
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s",
        level=getattr(logging, level.upper(), logging.INFO)
    )
