from news_fetcher import fetch_news_summary
from notifier import send_signal_notification

def generate_signal(pair, df, indicators):
    rsi = indicators.get("RSI")
    macd = indicators.get("MACD")
    boll = indicators.get("BOLL")

    confidence = 0
    if rsi < 40:
        confidence += 30
    if macd == "bullish":
        confidence += 30
    if boll == "lower breakout":
        confidence += 20

    if confidence < 70:
        return None

    entry = round(df["close"].iloc[-1], 2)
    stop = round(entry * 0.98, 2)
    target = round(entry * 1.04, 2)
    risk_reward = round((target - entry) / (entry - stop), 2)
    profit_percent = round((target - entry) / entry * 100, 2)
    profit_usdt = round(profit_percent * 3, 2)

    news = fetch_news_summary(pair)

    signal = {
        "symbol": pair,
        "strategy": "Day Trade",
        "timeframe": "1H",
        "entry_price": entry,
        "target_price": target,
        "stop_loss": stop,
        "risk_reward": risk_reward,
        "expected_profit_percent": profit_percent,
        "expected_profit_usdt": profit_usdt,
        "confidence_score": confidence,
        "indicators": [f"RSI ({rsi})", f"MACD ({macd})", f"Bollinger ({boll})"],
        "news_summary": news,
        "signal_type": "BUY",
        "volatility_alert": False,
        "created_at": df['timestamp'].iloc[-1].strftime("%d/%m/%Y %H:%M (UTC)")
    }

    send_signal_notification(signal)
    return signal

# Alias para manter compatibilidade com scanner.py
analisar_sinal = generate_signal
