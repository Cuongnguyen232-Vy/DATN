# -*- coding: utf-8 -*-
"""
VQuant Central Configuration Module
Loads settings from environment variables and .env file.
"""

import os

# Base Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
WEIGHTS_DIR = os.path.join(DATA_DIR, 'weights')
LOGS_DIR = os.path.join(DATA_DIR, 'logs')


def _load_env_file(filepath: str) -> None:
    """Zero-dependency .env file parser."""
    if not os.path.exists(filepath):
        return
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                k, v = line.split('=', 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k not in os.environ:
                    os.environ[k] = v
    except Exception as e:
        print(f"[Config] Canh bao load .env: {e}")


# Auto load .env from project root
_load_env_file(os.path.join(BASE_DIR, '.env'))

# MT5 Connection
MT5_PATH = os.getenv("MT5_TERMINAL_PATH", r"C:\Program Files\MetaTrader 5\terminal64.exe")

# Trading Constants
SYMBOL = os.getenv("SYMBOL", "XAUUSDm")
TIME_STEPS = 50

# Model & Storage Paths
MODEL_PATH = os.path.join(WEIGHTS_DIR, 'model_real.h5')
SCALER_PATH = os.path.join(WEIGHTS_DIR, 'scaler.save')
LOG_FILE = os.path.join(LOGS_DIR, 'System_logs.csv')

# Common MetaQuotes Communication Directory
app_data = os.getenv('APPDATA') or os.path.expanduser('~')
COMMON_FILES_PATH = os.path.join(app_data, "MetaQuotes", "Terminal", "Common", "Files")
SIGNAL_FILE = os.path.join(COMMON_FILES_PATH, f"vc_signal_{SYMBOL}.txt")

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8917012790:AAEqBr9UO-6lSYKNr2MtBpnx5tOjlmly2NE")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "5831996854")

# External News APIs
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
NEWSAPI_API_KEY = os.getenv("NEWSAPI_API_KEY", "")
