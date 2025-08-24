# -*- coding: utf-8 -*-
import json
from coingecko_client import get_prices_change_bulk, get_ohlc
from config import TOP_SYMBOLS

# Lista completa de pares monitorados (você pode editar à vontade)
SYMBOLS = [
    "BTCUSDT","ETHUSDT","BNBUSDT","XRPUSDT","ADAUSDT",
    "SOLUSDT","DOGEUSDT","MATICUSDT","DOTUSDT","LTCUSDT"
]

def main():
    print("🧩 Coletando PREÇOS em lote (bulk)…")
    prices = get_prices_change_bulk(SYMBOLS)  # 1..N chamadas (em lotes)

    # Escolhe os TOP_SYMBOLS por variação absoluta 24h
    ranked = []
    for sym in SYMBOLS:
        info = prices.get(sym)
        if info:
            ranked.append((sym, abs(info.get("change24h", 0.0))))
    ranked.sort(key=lambda x: x[1], reverse=True)

    selected = [sym for sym, _ in ranked[:max(1, TOP_SYMBOLS)]]
    print(f"✅ Selecionados para OHLC: {', '.join(selected)}")

    all_data = []
    for s in selected:
        print(f"📊 Coletando OHLC {s}…")
        try:
            ohlc = get_ohlc(s, days=1, vs_currency="usd")
            price = prices.get(s)
            if price and ohlc:
                all_data.append({"symbol": s, "price": price, "ohlc": ohlc})
                print(f"   → OK | candles={len(ohlc)}")
            else:
                print(f"   → ❌ Dados insuficientes para {s}")
        except Exception as e:
            print(f"   → ⚠️ Erro {s}: {e}")

    with open("data_raw.json","w") as f:
        json.dump(all_data, f, indent=2)
    print(f"💾 Salvo data_raw.json ({len(all_data)} ativos)")
    if not all_data:
        print("⚠️ Nenhum ativo coletado nesta rodada. Tente aumentar API_DELAY_SEC ou reduzir TOP_SYMBOLS.")

if __name__ == "__main__":
    main()
