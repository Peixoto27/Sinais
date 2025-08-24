# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
load_dotenv()

# Qualidade / Debug
MIN_CONFIDENCE = float(os.getenv("MIN_CONFIDENCE", "0.50"))
DEBUG_SCORE    = os.getenv("DEBUG_SCORE", "true").lower() == "true"
LOG_LEVEL      = os.getenv("LOG_LEVEL", "INFO").upper()

# Seleção de pares
SYMBOLS = [s.strip() for s in os.getenv(
    "SYMBOLS",
    "BTCUSDT,ETHUSDT,BNBUSDT,XRPUSDT,ADAUSDT,DOGEUSDT,SOLUSDT,MATICUSDT,DOTUSDT,LTCUSDT,LINKUSDT"
).split(",") if s.strip()]
TOP_SYMBOLS = int(os.getenv("TOP_SYMBOLS", "20"))

# CoinGecko – limites
API_DELAY_BULK  = float(os.getenv("API_DELAY_BULK", 2.5))
API_DELAY_OHLC  = float(os.getenv("API_DELAY_OHLC", 12.0))
MAX_RETRIES     = int(os.getenv("MAX_RETRIES", 6))
BACKOFF_BASE    = float(os.getenv("BACKOFF_BASE", 2.5))

# OHLC / histórico
OHLC_DAYS = int(os.getenv("OHLC_DAYS", "14"))   # 1,7,14,30,90,180,365
MIN_BARS  = int(os.getenv("MIN_BARS", "40"))    # mínimo de candles p/ score

# Batching
BATCH_OHLC      = int(os.getenv("BATCH_OHLC", 8))
BATCH_PAUSE_SEC = int(os.getenv("BATCH_PAUSE_SEC", 60))

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", os.getenv("BOT_TOKEN", ""))
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID", os.getenv("CHAT_ID", ""))

# Arquivos
DATA_RAW_FILE = os.getenv("DATA_RAW_FILE", "data_raw.json")
SIGNALS_FILE  = os.getenv("SIGNALS_FILE",  "signals.json")
HISTORY_FILE  = os.getenv("HISTORY_FILE",  "history.json")

# IA
USE_AI       = os.getenv("USE_AI", "true").lower() == "true"
AI_THRESHOLD = float(os.getenv("AI_THRESHOLD", "0.55"))
MODEL_FILE   = os.getenv("MODEL_FILE", "model.pkl")

# Anti-duplicado / updates
COOLDOWN_HOURS       = float(os.getenv("COOLDOWN_HOURS", "6"))
CHANGE_THRESHOLD_PCT = float(os.getenv("CHANGE_THRESHOLD_PCT", "1.0"))
SEND_STATUS_UPDATES  = os.getenv("SEND_STATUS_UPDATES", "true").lower() == "true"
