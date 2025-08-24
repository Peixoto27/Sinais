# sentiment_analyzer.py — versão final compatível com news_fetcher.get_recent_news(symbol)
import os
import time
from collections import deque
from typing import List, Optional

from textblob import TextBlob
from news_fetcher import get_recent_news  # assinatura: get_recent_news(symbol)

# ========================
# Configs (ajustáveis via env)
# ========================
HOURLY_API_CALL_LIMIT = int(os.getenv("SENTI_HOURLY_LIMIT", "10"))          # chamadas/hora
CACHE_DURATION        = int(os.getenv("SENTI_CACHE_SECONDS", str(2*60*60))) # 2h padrão
STALE_GRACE_SECONDS   = int(os.getenv("SENTI_STALE_GRACE", str(24*60*60)))  # cache vencido permitido por +24h
MIN_NEWS_FOR_SIGNAL   = int(os.getenv("SENTI_MIN_NEWS", "2"))               # mínimo p/ média; senão neutro

# ========================
# Estado
# ========================
api_call_timestamps: deque[float] = deque()
sentiment_cache = {}  # { symbol: {"score": float, "timestamp": float } }

# Mapa opcional (apenas para logs bonitos)
_SYMBOL_MAP = {
    "BTCUSDT": "Bitcoin",      "ETHUSDT": "Ethereum",     "BNBUSDT": "Binance Coin",
    "SOLUSDT": "Solana",       "XRPUSDT": "XRP",          "ADAUSDT": "Cardano",
    "AVAXUSDT": "Avalanche",   "DOTUSDT": "Polkadot",     "LINKUSDT": "Chainlink",
    "TONUSDT": "Toncoin",      "INJUSDT": "Injective",    "RNDRUSDT": "Render Token",
    "ARBUSDT": "Arbitrum",     "LTCUSDT": "Litecoin",     "MATICUSDT": "Polygon",
    "OPUSDT": "Optimism",      "NEARUSDT": "NEAR",        "APTUSDT": "Aptos",
    "PEPEUSDT": "Pepe",        "SEIUSDT": "Sei",          "TRXUSDT": "TRON",
    "DOGEUSDT": "Dogecoin",    "SHIBUSDT": "Shiba Inu",   "FILUSDT": "Filecoin",
    "SUIUSDT": "Sui",
}

def _nice(symbol: str) -> str:
    return _SYMBOL_MAP.get(symbol, symbol)

def _now() -> float:
    return time.time()

def can_make_api_call() -> bool:
    """Janela deslizante de 1h para respeitar limite de chamadas."""
    now = _now()
    while api_call_timestamps and api_call_timestamps[0] < now - 3600:
        api_call_timestamps.popleft()
    if len(api_call_timestamps) < HOURLY_API_CALL_LIMIT:
        return True
    print("🚦 Limite/hora atingido. Usando fallback/cache.")
    return False

def _dedupe_texts(texts: List[str]) -> List[str]:
    seen = set()
    unique = []
    for t in texts or []:
        t = (t or "").strip()
        if not t:
            continue
        key = t.lower()
        if key not in seen:
            seen.add(key)
            unique.append(t)
    return unique

def _compute_polarity(texts: List[str]) -> float:
    if not texts:
        return 0.0
    total, n = 0.0, 0
    for t in texts:
        try:
            total += TextBlob(t).sentiment.polarity  # [-1, 1]
            n += 1
        except Exception:
            continue
    if n == 0:
        return 0.0
    score = total / n
    if abs(score) < 0.05:  # reduz ruído
        score = 0.0
    return round(max(-1.0, min(1.0, score)), 2)

def _get_cache(symbol: str, now: float) -> Optional[float]:
    item = sentiment_cache.get(symbol)
    if not item:
        return None
    age = now - item["timestamp"]
    if age < CACHE_DURATION:
        print(f"🧠 Sentimento (cache válido) {symbol}: {item['score']:.2f}")
        return item["score"]
    return None

def _get_stale_if_allowed(symbol: str, now: float) -> Optional[float]:
    item = sentiment_cache.get(symbol)
    if not item:
        return None
    age = now - item["timestamp"]
    if age < CACHE_DURATION + STALE_GRACE_SECONDS:
        print(f"🧠 Sentimento (cache *stale* usado) {symbol}: {item['score']:.2f}")
        return item["score"]
    return None

def get_sentiment_score(symbol: str) -> float:
    """
    Retorna o sentimento médio [-1..1] para o símbolo.
    - Usa cache fresco quando disponível
    - Respeita cota/hora
    - Se NewsAPI falhar ou limite estourar, usa cache 'stale' (até 24h) ou 0.0
    """
    now = _now()

    # 1) cache fresco
    cached = _get_cache(symbol, now)
    if cached is not None:
        return cached

    # 2) cota
    if not can_make_api_call():
        stale = _get_stale_if_allowed(symbol, now)
        return stale if stale is not None else 0.0

    # 3) consulta notícias (usa assinatura do seu news_fetcher)
    api_call_timestamps.append(now)
    try:
        print(f"🌐 Buscando notícias para {_nice(symbol)} ({symbol}) …")
        titles = get_recent_news(symbol)  # <- usa a função que você já tem
        titles = _dedupe_texts(titles)

        if len(titles) < MIN_NEWS_FOR_SIGNAL:
            score = 0.0
        else:
            score = _compute_polarity(titles)

        print(f"🧠 Sentimento calculado {symbol}: {score:.2f}")
        sentiment_cache[symbol] = {"score": score, "timestamp": now}
        return score

    except Exception as e:
        print(f"⚠️ Falha ao buscar notícias para {symbol}: {e}")
        stale = _get_stale_if_allowed(symbol, now)
        if stale is not None:
            return stale
        return 0.0
