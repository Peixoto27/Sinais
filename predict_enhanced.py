# -*- coding: utf-8 -*-
"""
Script para fazer predições usando o modelo treinado
"""
import os, json, joblib, numpy as np
from datetime import datetime
from indicators import rsi, macd, ema, bollinger
import pandas as pd

MODEL_FILE = "model_enhanced.pkl"
SCALER_FILE = "scaler.pkl"

def load_model_and_scaler():
    """Carrega modelo e scaler treinados"""
    if not os.path.exists(MODEL_FILE) or not os.path.exists(SCALER_FILE):
        return None, None
    
    model = joblib.load(MODEL_FILE)
    scaler = joblib.load(SCALER_FILE)
    return model, scaler

def calculate_features_for_prediction(ohlc_data):
    """Calcula features para predição a partir dos dados OHLC"""
    if len(ohlc_data) < 60:
        return None
    
    # Extrair preços
    closes = [candle['close'] for candle in ohlc_data]
    highs = [candle['high'] for candle in ohlc_data]
    lows = [candle['low'] for candle in ohlc_data]
    
    # Calcular indicadores
    rsi_values = rsi(closes, 14)
    macd_line, signal_line, histogram = macd(closes, 12, 26, 9)
    ema20 = ema(closes, 20)
    ema50 = ema(closes, 50)
    bb_upper, bb_middle, bb_lower = bollinger(closes, 20, 2.0)
    
    # Indicadores adicionais
    sma10 = pd.Series(closes).rolling(10).mean().tolist()
    price_change = [(closes[i] - closes[i-1]) / closes[i-1] * 100 if i > 0 else 0 for i in range(len(closes))]
    volatility = pd.Series(closes).rolling(20).std().tolist()
    
    # Usar último ponto para predição
    i = -1  # Último índice
    
    if (rsi_values[i] is None or macd_line[i] is None or 
        ema20[i] is None or bb_upper[i] is None):
        return None
    
    features = [
        rsi_values[i],
        macd_line[i],
        signal_line[i] if signal_line[i] is not None else 0,
        histogram[i] if histogram[i] is not None else 0,
        ema20[i],
        ema50[i] if ema50[i] is not None else ema20[i],
        bb_upper[i],
        bb_middle[i],
        bb_lower[i],
        sma10[i] if sma10[i] is not None else closes[i],
        price_change[i],
        volatility[i] if volatility[i] is not None else 0,
    ]
    
    # Features de contexto
    current_price = closes[i]
    features.extend([
        current_price / ema20[i] - 1,  # Distância da EMA20
        current_price / bb_middle[i] - 1,  # Posição nas Bollinger Bands
        (bb_upper[i] - bb_lower[i]) / bb_middle[i],  # Largura das BB
    ])
    
    return np.array(features).reshape(1, -1)

def predict_signal(symbol, ohlc_data):
    """Faz predição para um símbolo específico"""
    model, scaler = load_model_and_scaler()
    if model is None or scaler is None:
        return None, "Modelo não encontrado"
    
    features = calculate_features_for_prediction(ohlc_data)
    if features is None:
        return None, "Dados insuficientes para predição"
    
    # Normalizar features
    features_scaled = scaler.transform(features)
    
    # Fazer predição
    prediction = model.predict(features_scaled)[0]
    probability = model.predict_proba(features_scaled)[0]
    
    confidence = max(probability)
    signal = "COMPRA" if prediction == 1 else "VENDA"
    
    return {
        'symbol': symbol,
        'signal': signal,
        'confidence': float(confidence),
        'probability_buy': float(probability[1]),
        'probability_sell': float(probability[0]),
        'timestamp': datetime.now().isoformat()
    }, None

def test_predictions():
    """Testa predições com dados atuais"""
    print("🔮 Testando predições do modelo...")
    
    # Carregar dados atuais
    if not os.path.exists("data_raw.json"):
        print("❌ Arquivo data_raw.json não encontrado")
        return
    
    with open("data_raw.json", 'r') as f:
        raw_data = json.load(f)
    
    predictions = []
    
    for asset_data in raw_data:
        symbol = asset_data['symbol']
        ohlc = asset_data['ohlc']
        
        result, error = predict_signal(symbol, ohlc)
        
        if result:
            predictions.append(result)
            print(f"📊 {symbol}: {result['signal']} (confiança: {result['confidence']:.3f})")
        else:
            print(f"❌ {symbol}: {error}")
    
    # Salvar predições
    with open("predictions.json", 'w') as f:
        json.dump(predictions, f, indent=2)
    
    print(f"💾 Predições salvas em predictions.json")
    return predictions

if __name__ == "__main__":
    test_predictions()

