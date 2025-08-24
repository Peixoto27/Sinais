# -*- coding: utf-8 -*-
"""
Script de validação e backtesting do modelo de trading
"""
import os, json, joblib, numpy as np, pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc
from indicators import rsi, macd, ema, bollinger

MODEL_FILE = "model_enhanced.pkl"
SCALER_FILE = "scaler.pkl"
DATA_RAW_FILE = "data_raw.json"

def load_model_and_data():
    """Carrega modelo, scaler e dados"""
    model = joblib.load(MODEL_FILE)
    scaler = joblib.load(SCALER_FILE)
    
    with open(DATA_RAW_FILE, 'r') as f:
        raw_data = json.load(f)
    
    return model, scaler, raw_data

def calculate_features_for_validation(ohlc_data):
    """Calcula features para validação (similar ao treinamento)"""
    if len(ohlc_data) < 60:
        return None, None
    
    closes = [candle['close'] for candle in ohlc_data]
    
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
    
    features_list = []
    targets_list = []
    timestamps = []
    
    # Criar features para cada ponto temporal
    for i in range(30, len(closes) - 5):  # -5 para ter dados futuros
        if (rsi_values[i] is not None and macd_line[i] is not None and
            ema20[i] is not None and bb_upper[i] is not None):
            
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
                current_price / ema20[i] - 1,
                current_price / bb_middle[i] - 1,
                (bb_upper[i] - bb_lower[i]) / bb_middle[i],
            ])
            
            # Target real (movimento futuro)
            future_prices = closes[i+1:i+6]
            future_return = (max(future_prices) - current_price) / current_price
            target = 1 if future_return > 0.02 else 0
            
            features_list.append(features)
            targets_list.append(target)
            timestamps.append(i)
    
    return np.array(features_list), np.array(targets_list), timestamps

def backtest_strategy(model, scaler, raw_data):
    """Executa backtesting da estratégia"""
    print("📈 Executando backtesting...")
    
    all_predictions = []
    all_targets = []
    all_returns = []
    trades = []
    
    for asset_data in raw_data:
        symbol = asset_data['symbol']
        ohlc = asset_data['ohlc']
        
        features, targets, timestamps = calculate_features_for_validation(ohlc)
        if features is None or len(features) == 0:
            continue
        
        # Fazer predições
        features_scaled = scaler.transform(features)
        predictions = model.predict(features_scaled)
        probabilities = model.predict_proba(features_scaled)
        
        closes = [candle['close'] for candle in ohlc]
        
        # Simular trades
        for i, (pred, prob, target, ts) in enumerate(zip(predictions, probabilities, targets, timestamps)):
            confidence = max(prob)
            
            if confidence > 0.6:  # Só fazer trade com alta confiança
                entry_price = closes[ts]
                
                # Simular resultado do trade (próximos 5 períodos)
                if ts + 5 < len(closes):
                    future_prices = closes[ts+1:ts+6]
                    if pred == 1:  # Compra
                        exit_price = max(future_prices)
                        trade_return = (exit_price - entry_price) / entry_price
                    else:  # Venda (short)
                        exit_price = min(future_prices)
                        trade_return = (entry_price - exit_price) / entry_price
                    
                    trades.append({
                        'symbol': symbol,
                        'prediction': pred,
                        'confidence': confidence,
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'return': trade_return,
                        'target': target,
                        'timestamp': ts
                    })
                    
                    all_returns.append(trade_return)
        
        all_predictions.extend(predictions)
        all_targets.extend(targets)
    
    return trades, all_predictions, all_targets, all_returns

def create_performance_report(trades, predictions, targets, returns):
    """Cria relatório de performance"""
    print("\n📊 RELATÓRIO DE PERFORMANCE")
    print("=" * 50)
    
    # Métricas básicas
    total_trades = len(trades)
    winning_trades = len([t for t in trades if t['return'] > 0])
    win_rate = winning_trades / total_trades if total_trades > 0 else 0
    
    avg_return = np.mean(returns) if returns else 0
    total_return = np.sum(returns) if returns else 0
    max_return = max(returns) if returns else 0
    min_return = min(returns) if returns else 0
    
    print(f"📈 Total de trades: {total_trades}")
    print(f"🎯 Taxa de acerto: {win_rate:.2%}")
    print(f"💰 Retorno médio por trade: {avg_return:.2%}")
    print(f"📊 Retorno total: {total_return:.2%}")
    print(f"🚀 Melhor trade: {max_return:.2%}")
    print(f"📉 Pior trade: {min_return:.2%}")
    
    # Métricas de classificação
    print(f"\n🤖 MÉTRICAS DO MODELO")
    print("=" * 30)
    print(classification_report(targets, predictions))
    
    # Análise por símbolo
    print(f"\n📋 PERFORMANCE POR SÍMBOLO")
    print("=" * 35)
    
    symbol_stats = {}
    for trade in trades:
        symbol = trade['symbol']
        if symbol not in symbol_stats:
            symbol_stats[symbol] = {'trades': [], 'returns': []}
        symbol_stats[symbol]['trades'].append(trade)
        symbol_stats[symbol]['returns'].append(trade['return'])
    
    for symbol, stats in symbol_stats.items():
        symbol_trades = len(stats['trades'])
        symbol_wins = len([t for t in stats['trades'] if t['return'] > 0])
        symbol_win_rate = symbol_wins / symbol_trades if symbol_trades > 0 else 0
        symbol_avg_return = np.mean(stats['returns']) if stats['returns'] else 0
        
        print(f"{symbol}: {symbol_trades} trades, {symbol_win_rate:.1%} win rate, {symbol_avg_return:.2%} avg return")
    
    return {
        'total_trades': total_trades,
        'win_rate': win_rate,
        'avg_return': avg_return,
        'total_return': total_return,
        'symbol_stats': symbol_stats
    }

def create_visualizations(trades, predictions, targets, returns):
    """Cria visualizações da performance"""
    print("\n📊 Criando visualizações...")
    
    plt.style.use('default')
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Análise de Performance do Modelo de Trading', fontsize=16, fontweight='bold')
    
    # 1. Distribuição de retornos
    axes[0, 0].hist(returns, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
    axes[0, 0].axvline(0, color='red', linestyle='--', alpha=0.7)
    axes[0, 0].set_title('Distribuição de Retornos por Trade')
    axes[0, 0].set_xlabel('Retorno (%)')
    axes[0, 0].set_ylabel('Frequência')
    
    # 2. Matriz de confusão
    cm = confusion_matrix(targets, predictions)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[0, 1])
    axes[0, 1].set_title('Matriz de Confusão')
    axes[0, 1].set_xlabel('Predição')
    axes[0, 1].set_ylabel('Real')
    
    # 3. Retornos cumulativos
    cumulative_returns = np.cumsum(returns)
    axes[1, 0].plot(cumulative_returns, color='green', linewidth=2)
    axes[1, 0].axhline(0, color='red', linestyle='--', alpha=0.7)
    axes[1, 0].set_title('Retornos Cumulativos')
    axes[1, 0].set_xlabel('Trade #')
    axes[1, 0].set_ylabel('Retorno Cumulativo (%)')
    axes[1, 0].grid(True, alpha=0.3)
    
    # 4. Performance por símbolo
    symbol_returns = {}
    for trade in trades:
        symbol = trade['symbol']
        if symbol not in symbol_returns:
            symbol_returns[symbol] = []
        symbol_returns[symbol].append(trade['return'])
    
    symbols = list(symbol_returns.keys())
    avg_returns = [np.mean(symbol_returns[s]) * 100 for s in symbols]
    
    bars = axes[1, 1].bar(symbols, avg_returns, color=['green' if r > 0 else 'red' for r in avg_returns])
    axes[1, 1].set_title('Retorno Médio por Símbolo')
    axes[1, 1].set_xlabel('Símbolo')
    axes[1, 1].set_ylabel('Retorno Médio (%)')
    axes[1, 1].tick_params(axis='x', rotation=45)
    
    # Adicionar valores nas barras
    for bar, value in zip(bars, avg_returns):
        height = bar.get_height()
        axes[1, 1].text(bar.get_x() + bar.get_width()/2., height + (0.1 if height > 0 else -0.3),
                       f'{value:.1f}%', ha='center', va='bottom' if height > 0 else 'top')
    
    plt.tight_layout()
    plt.savefig('model_performance.png', dpi=300, bbox_inches='tight')
    print("💾 Gráficos salvos em model_performance.png")
    
    return fig

def main():
    print("🔍 Iniciando validação do modelo...")
    
    # Carregar modelo e dados
    model, scaler, raw_data = load_model_and_data()
    
    # Executar backtesting
    trades, predictions, targets, returns = backtest_strategy(model, scaler, raw_data)
    
    if not trades:
        print("❌ Nenhum trade foi executado no backtesting")
        return
    
    # Criar relatório
    performance = create_performance_report(trades, predictions, targets, returns)
    
    # Criar visualizações
    fig = create_visualizations(trades, predictions, targets, returns)
    
    # Salvar resultados detalhados
    results = {
        'performance_summary': performance,
        'trades': trades,
        'timestamp': datetime.now().isoformat()
    }
    
    with open('backtest_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("💾 Resultados salvos em backtest_results.json")
    print("✅ Validação concluída!")

if __name__ == "__main__":
    main()

