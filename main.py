# -*- coding: utf-8 -*-
"""
API Flask para Sistema de Trading de Criptomoedas com IA
"""
import os
import sys
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import json
import joblib
import numpy as np
from datetime import datetime
import threading
import time

# Adicionar diretório atual ao path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Imports do projeto
try:
    from predict_enhanced import predict_signal, load_model_and_scaler
    from coingecko_client import fetch_bulk_prices, fetch_ohlc, SYMBOL_TO_ID
    from config import SYMBOLS
except ImportError as e:
    print(f"Erro ao importar módulos: {e}")

app = Flask(__name__)
CORS(app)  # Permitir CORS para todas as rotas

# Variáveis globais para cache
predictions_cache = {}
last_update = None
model = None
scaler = None

def load_ai_model():
    """Carrega o modelo de IA"""
    global model, scaler
    try:
        model, scaler = load_model_and_scaler()
        if model is not None:
            print("✅ Modelo de IA carregado com sucesso")
            return True
        else:
            print("❌ Falha ao carregar modelo de IA")
            return False
    except Exception as e:
        print(f"❌ Erro ao carregar modelo: {e}")
        return False

def collect_and_predict():
    """Coleta dados e faz predições"""
    global predictions_cache, last_update
    
    try:
        print("🔄 Coletando dados e fazendo predições...")
        
        # Coletar dados de preços
        bulk_data = fetch_bulk_prices(SYMBOLS)
        predictions = []
        
        for symbol in SYMBOLS:
            try:
                # Obter dados OHLC
                coin_id = SYMBOL_TO_ID.get(symbol, symbol.replace("USDT", "").lower())
                ohlc_data = fetch_ohlc(coin_id, days=30)
                
                if not ohlc_data or len(ohlc_data) < 60:
                    continue
                
                # Converter para formato esperado
                candles = []
                for ts, o, h, l, c in ohlc_data:
                    candles.append({
                        "timestamp": int(ts/1000),
                        "open": float(o),
                        "high": float(h),
                        "low": float(l),
                        "close": float(c)
                    })
                
                # Fazer predição
                result, error = predict_signal(symbol, candles)
                
                if result:
                    # Adicionar dados de preço atual
                    current_data = bulk_data.get(symbol, {})
                    result.update({
                        'current_price': current_data.get('usd', 0),
                        'price_change_24h': current_data.get('usd_24h_change', 0),
                        'market_cap': current_data.get('usd_market_cap', 0)
                    })
                    predictions.append(result)
                    
            except Exception as e:
                print(f"❌ Erro ao processar {symbol}: {e}")
                continue
        
        predictions_cache = predictions
        last_update = datetime.now()
        print(f"✅ Predições atualizadas: {len(predictions)} símbolos")
        
    except Exception as e:
        print(f"❌ Erro na coleta de dados: {e}")

def background_updater():
    """Atualiza predições em background"""
    while True:
        try:
            collect_and_predict()
            time.sleep(300)  # Atualizar a cada 5 minutos
        except Exception as e:
            print(f"❌ Erro no background updater: {e}")
            time.sleep(60)  # Tentar novamente em 1 minuto

@app.route('/')
def index():
    """Página principal com interface web"""
    html_template = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🚀 Crypto Trading AI - Sinais de Trading</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            .container { 
                max-width: 1200px; 
                margin: 0 auto; 
                padding: 20px;
            }
            .header {
                text-align: center;
                color: white;
                margin-bottom: 30px;
            }
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .stat-card {
                background: white;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 8px 25px rgba(0,0,0,0.1);
                text-align: center;
            }
            .stat-value {
                font-size: 2em;
                font-weight: bold;
                color: #667eea;
            }
            .signals-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 20px;
            }
            .signal-card {
                background: white;
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 8px 25px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }
            .signal-card:hover {
                transform: translateY(-5px);
            }
            .signal-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
            }
            .symbol {
                font-size: 1.5em;
                font-weight: bold;
                color: #333;
            }
            .signal-type {
                padding: 8px 16px;
                border-radius: 25px;
                color: white;
                font-weight: bold;
                font-size: 0.9em;
            }
            .buy { background: linear-gradient(45deg, #4CAF50, #45a049); }
            .sell { background: linear-gradient(45deg, #f44336, #da190b); }
            .confidence {
                font-size: 1.2em;
                font-weight: bold;
                margin: 10px 0;
            }
            .high-confidence { color: #4CAF50; }
            .medium-confidence { color: #FF9800; }
            .low-confidence { color: #f44336; }
            .price-info {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
                margin: 15px 0;
            }
            .price-item {
                text-align: center;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 8px;
            }
            .price-label {
                font-size: 0.8em;
                color: #666;
                margin-bottom: 5px;
            }
            .price-value {
                font-weight: bold;
                color: #333;
            }
            .timestamp {
                text-align: center;
                color: #666;
                font-size: 0.9em;
                margin-top: 15px;
                padding-top: 15px;
                border-top: 1px solid #eee;
            }
            .loading {
                text-align: center;
                color: white;
                font-size: 1.2em;
                margin: 50px 0;
            }
            .refresh-btn {
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 25px;
                cursor: pointer;
                font-size: 1em;
                margin: 20px auto;
                display: block;
                transition: transform 0.3s ease;
            }
            .refresh-btn:hover {
                transform: scale(1.05);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Crypto Trading AI</h1>
                <p>Sistema Inteligente de Sinais de Trading para Criptomoedas</p>
            </div>
            
            <div class="stats" id="stats">
                <div class="stat-card">
                    <div class="stat-value" id="total-signals">-</div>
                    <div>Total de Sinais</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="buy-signals">-</div>
                    <div>Sinais de Compra</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="sell-signals">-</div>
                    <div>Sinais de Venda</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="avg-confidence">-</div>
                    <div>Confiança Média</div>
                </div>
            </div>
            
            <button class="refresh-btn" onclick="loadPredictions()">🔄 Atualizar Sinais</button>
            
            <div class="loading" id="loading">Carregando sinais...</div>
            <div class="signals-grid" id="signals-grid"></div>
        </div>

        <script>
            async function loadPredictions() {
                document.getElementById('loading').style.display = 'block';
                document.getElementById('signals-grid').innerHTML = '';
                
                try {
                    const response = await fetch('/api/predictions');
                    const data = await response.json();
                    
                    if (data.success) {
                        displayPredictions(data.predictions);
                        updateStats(data.predictions);
                    } else {
                        document.getElementById('loading').innerHTML = '❌ Erro ao carregar sinais: ' + data.error;
                    }
                } catch (error) {
                    document.getElementById('loading').innerHTML = '❌ Erro de conexão: ' + error.message;
                }
            }
            
            function displayPredictions(predictions) {
                document.getElementById('loading').style.display = 'none';
                const grid = document.getElementById('signals-grid');
                
                if (predictions.length === 0) {
                    grid.innerHTML = '<div style="text-align: center; color: white; font-size: 1.2em;">Nenhum sinal disponível no momento</div>';
                    return;
                }
                
                predictions.forEach(pred => {
                    const card = createSignalCard(pred);
                    grid.appendChild(card);
                });
            }
            
            function createSignalCard(pred) {
                const card = document.createElement('div');
                card.className = 'signal-card';
                
                const confidenceClass = pred.confidence > 0.7 ? 'high-confidence' : 
                                      pred.confidence > 0.5 ? 'medium-confidence' : 'low-confidence';
                
                const signalClass = pred.signal === 'COMPRA' ? 'buy' : 'sell';
                const signalEmoji = pred.signal === 'COMPRA' ? '📈' : '📉';
                
                card.innerHTML = `
                    <div class="signal-header">
                        <div class="symbol">${pred.symbol}</div>
                        <div class="signal-type ${signalClass}">${signalEmoji} ${pred.signal}</div>
                    </div>
                    
                    <div class="confidence ${confidenceClass}">
                        Confiança: ${(pred.confidence * 100).toFixed(1)}%
                    </div>
                    
                    <div class="price-info">
                        <div class="price-item">
                            <div class="price-label">Preço Atual</div>
                            <div class="price-value">$${pred.current_price ? pred.current_price.toFixed(6) : 'N/A'}</div>
                        </div>
                        <div class="price-item">
                            <div class="price-label">Variação 24h</div>
                            <div class="price-value" style="color: ${pred.price_change_24h > 0 ? '#4CAF50' : '#f44336'}">
                                ${pred.price_change_24h ? pred.price_change_24h.toFixed(2) : 'N/A'}%
                            </div>
                        </div>
                    </div>
                    
                    <div class="price-info">
                        <div class="price-item">
                            <div class="price-label">Prob. Compra</div>
                            <div class="price-value">${(pred.probability_buy * 100).toFixed(1)}%</div>
                        </div>
                        <div class="price-item">
                            <div class="price-label">Prob. Venda</div>
                            <div class="price-value">${(pred.probability_sell * 100).toFixed(1)}%</div>
                        </div>
                    </div>
                    
                    <div class="timestamp">
                        ${new Date(pred.timestamp).toLocaleString('pt-BR')}
                    </div>
                `;
                
                return card;
            }
            
            function updateStats(predictions) {
                const total = predictions.length;
                const buySignals = predictions.filter(p => p.signal === 'COMPRA').length;
                const sellSignals = predictions.filter(p => p.signal === 'VENDA').length;
                const avgConfidence = predictions.reduce((sum, p) => sum + p.confidence, 0) / total;
                
                document.getElementById('total-signals').textContent = total;
                document.getElementById('buy-signals').textContent = buySignals;
                document.getElementById('sell-signals').textContent = sellSignals;
                document.getElementById('avg-confidence').textContent = (avgConfidence * 100).toFixed(1) + '%';
            }
            
            // Carregar sinais ao iniciar
            loadPredictions();
            
            // Atualizar automaticamente a cada 5 minutos
            setInterval(loadPredictions, 300000);
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route('/api/predictions')
def get_predictions():
    """API endpoint para obter predições"""
    try:
        global predictions_cache, last_update
        
        # Se não há cache ou está muito antigo, coletar novos dados
        if not predictions_cache or not last_update or \
           (datetime.now() - last_update).seconds > 300:
            collect_and_predict()
        
        return jsonify({
            'success': True,
            'predictions': predictions_cache,
            'last_update': last_update.isoformat() if last_update else None,
            'total_signals': len(predictions_cache)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/status')
def get_status():
    """Status da API"""
    return jsonify({
        'status': 'online',
        'model_loaded': model is not None,
        'last_update': last_update.isoformat() if last_update else None,
        'cached_predictions': len(predictions_cache)
    })

@app.route('/api/force-update')
def force_update():
    """Força atualização das predições"""
    try:
        collect_and_predict()
        return jsonify({
            'success': True,
            'message': 'Predições atualizadas com sucesso',
            'predictions_count': len(predictions_cache)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Iniciando Crypto Trading API...")
    
    # Carregar modelo de IA
    load_ai_model()
    
    # Fazer primeira coleta de dados
    collect_and_predict()
    
    # Iniciar thread de atualização em background
    updater_thread = threading.Thread(target=background_updater, daemon=True)
    updater_thread.start()
    
    print("✅ API iniciada com sucesso!")
    print("🌐 Acesse: http://localhost:5000")
    
    # Executar Flask
    app.run(host='0.0.0.0', port=5000, debug=False)

