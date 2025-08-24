import pandas as pd
import datetime
import uuid # Importar a biblioteca uuid

PONTUACAO_MINIMA_PARA_SINAL = 80 # Aumentar a pontuação mínima para sinais

PESO_SMA = 35
PESO_VOLUME = 30
PESO_MACD = 25
PESO_RSI = 10

def generate_signal(df_with_indicators, symbol):
    if df_with_indicators.empty:
        return None

    latest = df_with_indicators.iloc[-1]
    
    confidence_score = 0
    
    # Condições para sinais de compra
    # SMA: Preço acima da média móvel de 50 períodos
    if latest["close"] > latest["sma_50"]:
        confidence_score += PESO_SMA
        
    # Volume: Volume atual maior que a média móvel de 20 períodos do volume
    if latest["volume"] > latest["volume_sma_20"]:
        confidence_score += PESO_VOLUME
        
    # MACD: Linha MACD acima da linha de sinal (MACD Diff > 0)
    if latest["macd_diff"] > 0:
        confidence_score += PESO_MACD
        
    # RSI: RSI abaixo de 70 (não sobrecomprado)
    if latest["rsi"] < 70:
        confidence_score += PESO_RSI

    # Adicionar uma condição extra para PEPEUSDT para filtrar sinais de baixa qualidade
    if symbol == "PEPEUSDT":
        # Exemplo: Exigir que o RSI esteja entre 30 e 70 para PEPEUSDT
        if not (latest["rsi"] > 30 and latest["rsi"] < 70):
            confidence_score = 0 # Zera a pontuação se não atender a esta condição específica

    if confidence_score >= PONTUACAO_MINIMA_PARA_SINAL:
        entry_price = latest["close"]
        # Stop e alvo fixos, pois ATR não está disponível
        stop_loss = entry_price * 0.98 # Exemplo: 2% abaixo
        target_price = entry_price * 1.04 # Exemplo: 4% acima
        
        # Ajustar a formatação para moedas de baixo valor
        if entry_price < 0.001:
            price_format = ".8f"
        elif entry_price < 0.01:
            price_format = ".6f"
        elif entry_price < 1:
            price_format = ".4f"
        else:
            price_format = ".2f"

        signal_dict = {
            "id": str(uuid.uuid4()), # Adiciona um ID único ao sinal
            "signal_type": "BUY",
            "symbol": symbol,
            "entry_price": f"{entry_price:{price_format}}",
            "target_price": f"{target_price:{price_format}}",
            "stop_loss": f"{stop_loss:{price_format}}",
            "risk_reward": "1:2.0", # Mantido para consistência, mas baseado em % fixo
            "confidence_score": f"{confidence_score}",
            "strategy": f"IA-Weighted (Fixed Stop)", # Estratégia atualizada
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return signal_dict

    return None




