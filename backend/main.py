import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import pandas as pd
import pandas_ta as ta

app = Flask(__name__)
CORS(app)

def get_advanced_technical_analysis(symbol, timeframe='1d'):
    """
    Realiza uma análise técnica avançada com múltiplos indicadores e um score de confiança.
    """
    try:
        limit = 200  # Precisamos de mais dados para os cálculos
        url = f'https://api.binance.us/api/v3/klines?symbol={symbol}&interval={timeframe}&limit={limit}'
        response = requests.get(url )
        response.raise_for_status()
        data = response.json()

        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
        df['close'] = pd.to_numeric(df['close'])

        # --- 1. Calcular TODOS os indicadores ---
        df.ta.sma(length=10, append=True)
        df.ta.sma(length=30, append=True)
        df.ta.rsi(length=14, append=True)
        df.ta.macd(fast=12, slow=26, signal=9, append=True)
        df.ta.bbands(length=20, std=2, append=True)
        
        df.dropna(inplace=True)
        if df.empty: raise Exception("Dados insuficientes para análise.")

        last = df.iloc[-1]
        prev = df.iloc[-2]

        # --- 2. Calcular o Score de Confiança (de 0 a 10) ---
        buy_signals_score = 0
        sell_signals_score = 0

        # Sinal 1: Cruzamento de Médias Móveis (Peso: 3)
        if last['SMA_10'] > last['SMA_30'] and prev['SMA_10'] <= prev['SMA_30']: buy_signals_score += 3
        if last['SMA_10'] < last['SMA_30'] and prev['SMA_10'] >= prev['SMA_30']: sell_signals_score += 3

        # Sinal 2: MACD (Peso: 3)
        if last['MACD_12_26_9'] > last['MACDs_12_26_9'] and prev['MACD_12_26_9'] <= prev['MACDs_12_26_9']: buy_signals_score += 3
        if last['MACD_12_26_9'] < last['MACDs_12_26_9'] and prev['MACD_12_26_9'] >= prev['MACDs_12_26_9']: sell_signals_score += 3

        # Sinal 3: RSI (Peso: 2)
        if last['RSI_14'] < 40: buy_signals_score += 2
        if last['RSI_14'] > 60: sell_signals_score += 2

        # Sinal 4: Bandas de Bollinger (Peso: 2)
        if last['close'] <= last['BBL_20_2.0']: buy_signals_score += 2
        if last['close'] >= last['BBU_20_2.0']: sell_signals_score += 2

        # --- 3. Determinar o Sinal Final e o Score ---
        final_signal = "NEUTRAL"
        confidence_score = 0
        if buy_signals_score > sell_signals_score:
            final_signal = "BUY"
            confidence_score = min(buy_signals_score, 10)
        elif sell_signals_score > buy_signals_score:
            final_signal = "SELL"
            confidence_score = min(sell_signals_score, 10)

        if confidence_score < 7: # Requisito: só mostrar sinal se confiança >= 7
            final_signal = f"HOLD ({'Alta' if last['SMA_10'] > last['SMA_30'] else 'Baixa'})"

        return {
            "pair": symbol.replace("USDT", "/USDT"),
            "price": round(last['close'], 4),
            "signal": final_signal,
            "confidence": f"{confidence_score}/10",
            "indicators": {
                "rsi": round(last['RSI_14'], 2),
                "macd": round(last['MACD_12_26_9'], 2),
                "bollinger_upper": round(last['BBU_20_2.0'], 2),
                "bollinger_lower": round(last['BBL_20_2.0'], 2)
            }
        }
    except Exception as e:
        print(f"Erro em {symbol} ({timeframe}): {e}")
        return {"pair": symbol.replace("USDT", "/USDT"), "signal": "ERROR", "error_message": str(e)}

@app.route("/signals") # A única rota que precisamos agora
def get_pro_signals():
    timeframe = request.args.get('timeframe', '1d')
    symbols = ["BTCUSDT", "ETHUSDT", "XRPUSDT", "SOLUSDT", "ADAUSDT"]
    signals = [get_advanced_technical_analysis(s, timeframe) for s in symbols]
    return jsonify(signals)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
