import os
import json
import logging
import re
from pathlib import Path

# Setup App Data Directory
APP_NAME = "ScreenQR"
APP_DIR = Path.home() / f".{APP_NAME.lower()}"
CONFIG_FILE = APP_DIR / "config.json"
LOG_FILE = APP_DIR / "app.log"
HISTORY_FILE = APP_DIR / "history.json"

# Ensure app dir exists
APP_DIR.mkdir(parents=True, exist_ok=True)

# Configure Logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

DEFAULT_CONFIG = {
    "auto_copy": True,
    "dark_mode": True,
    "window_x": None,
    "window_y": None
}

def load_config() -> dict:
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # Merge with default in case of missing keys
            for k, v in DEFAULT_CONFIG.items():
                if k not in config:
                    config[k] = v
            return config
    except Exception as e:
        logging.error(f"Error loading config: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(config: dict):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        logging.error(f"Error saving config: {e}")

def load_history() -> list:
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading history: {e}")
        return []

def save_history(history: list):
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4)
    except Exception as e:
        logging.error(f"Error saving history: {e}")

def add_to_history(text: str):
    history = load_history()
    # Remove if it already exists to bring to top
    if text in history:
        history.remove(text)
    history.insert(0, text)
    # Keep only last 20
    history = history[:20]
    save_history(history)

def is_valid_url(text: str) -> bool:
    # Basic URL validation regex
    pattern = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(pattern, text) is not None
