# -*- coding: utf-8 -*-
import time
import random
import requests
from typing import List, Dict, Any

from config import (
    API_DELAY_BULK, API_DELAY_OHLC, MAX_RETRIES, BACKOFF_BASE
)

# Mapeia tickers (ex.: BTCUSDT) -> IDs do CoinGecko
SYMBOL_TO_ID: Dict[str, str] = {
    "BTCUSDT":  "bitcoin",
    "ETHUSDT":  "ethereum",
    "BNBUSDT":  "binancecoin",
    "XRPUSDT":  "ripple",
    "ADAUSDT":  "cardano",
    "SOLUSDT":  "solana",
    "DOGEUSDT": "dogecoin",
    "MATICUSDT":"matic-network",
    "DOTUSDT":  "polkadot",
    "LTCUSDT":  "litecoin",
    "LINKUSDT": "chainlink",
    "BCHUSDT":  "bitcoin-cash",
    "ATOMUSDT": "cosmos",
    "AVAXUSDT": "avalanche-2",
    "XLMUSDT":  "stellar",
    "FILUSDT":  "filecoin",
    "TRXUSDT":  "tron",
    "APTUSDT":  "aptos",
    "INJUSDT":  "injective-protocol",
    "ARBUSDT":  "arbitrum",
}

API_BASE = "https://api.coingecko.com/api/v3"

session = requests.Session()
session.headers.update({"User-Agent": "CryptonSignals/1.0 (Railway)"})


def _to_cg_id(sym_or_id: str) -> str:
    """Aceita BTCUSDT ou já um id do CG (ex.: bitcoin)"""
    s = sym_or_id.strip()
    return SYMBOL_TO_ID.get(s, s.replace("USDT", "").lower())


def fetch_bulk_prices(symbols: List[str]) -> Dict[str, Any]:
    """
    Busca preços em lote (simple/price).
    Entrada: lista de TICKERS (ex.: ["BTCUSDT","ETHUSDT",...]) OU ids.
    Retorno: dict mapeado pelo MESMO ticker de entrada:
        {"BTCUSDT": {"usd": 12345.0, "usd_24h_change": 1.23}, ...}
    """
    ids = ",".join(_to_cg_id(s) for s in symbols)
    url = f"{API_BASE}/simple/price"
    params = {"ids": ids, "vs_currencies": "usd", "include_24hr_change": "true"}

    # delay leve pré-chamada para espaçar execuções
    time.sleep(API_DELAY_BULK)

    resp = session.get(url, params=params, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    # re-mapeia para as chaves originais (tickers)
    out: Dict[str, Any] = {}
    for s in symbols:
        cid = _to_cg_id(s)
        if cid in data:
            out[s] = data[cid]
    return out


def fetch_ohlc(sym_or_id: str, days: int = 1) -> list:
    """
    Busca OHLC com retry/backoff e respeito ao Retry-After.
    Aceita TICKER ou ID. Retorna a lista crua do CG:
        [[ts, open, high, low, close], ...]
    """
    coin_id = _to_cg_id(sym_or_id)
    url = f"{API_BASE}/coins/{coin_id}/ohlc"
    params = {"vs_currency": "usd", "days": days}

    delay = API_DELAY_OHLC
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = session.get(url, params=params, timeout=25)
            # Sucesso
            if resp.status_code == 200:
                # delay pós-sucesso (mantém espaçamento)
                time.sleep(API_DELAY_OHLC + random.uniform(0.4, 1.6))
                return resp.json()

            # Rate limit
            if resp.status_code == 429:
                retry_after = resp.headers.get("Retry-After")
                wait = float(retry_after) if retry_after else delay
                wait += random.uniform(0.8, 2.0)
                print(f"⚠️ 429 OHLC {coin_id}: aguardando {round(wait,1)}s (tentativa {attempt}/{MAX_RETRIES})")
                time.sleep(wait)
                delay = min(delay * BACKOFF_BASE, 60.0)
                continue

            # 5xx: tenta novamente com backoff
            if 500 <= resp.status_code < 600:
                wait = delay + random.uniform(0.8, 2.0)
                print(f"⚠️ {resp.status_code} OHLC {coin_id}: aguardando {round(wait,1)}s")
                time.sleep(wait)
                delay = min(delay * BACKOFF_BASE, 60.0)
                continue

            # Qualquer outro erro
            resp.raise_for_status()

        except requests.RequestException as e:
            wait = delay + random.uniform(0.8, 2.0)
            print(f"⚠️ Erro OHLC {coin_id}: {e} (tentativa {attempt}/{MAX_RETRIES}). Aguardando {round(wait,1)}s")
            time.sleep(wait)
            delay = min(delay * BACKOFF_BASE, 60.0)

    # Estourou as tentativas
    return []
