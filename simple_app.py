# -*- coding: utf-8 -*-
"""
Versão simplificada da API Flask para teste
"""
from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Dados de exemplo para teste
sample_predictions = [
    {
        "symbol": "BTCUSDT",
        "signal": "VENDA",
        "confidence": 0.99,
        "probability_buy": 0.01,
        "probability_sell": 0.99,
        "current_price": 116834.0,
        "price_change_24h": -2.5,
        "timestamp": datetime.now().isoformat()
    },
    {
        "symbol": "DOGEUSDT", 
        "signal": "COMPRA",
        "confidence": 0.96,
        "probability_buy": 0.96,
        "probability_sell": 0.04,
        "current_price": 0.240619,
        "price_change_24h": 5.2,
        "timestamp": datetime.now().isoformat()
    },
    {
        "symbol": "PEPEUSDT",
        "signal": "COMPRA", 
        "confidence": 0.54,
        "probability_buy": 0.54,
        "probability_sell": 0.46,
        "current_price": 0.00001158,
        "price_change_24h": 3.1,
        "timestamp": datetime.now().isoformat()
    }
]

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
                <p><strong>Status:</strong> ✅ Online | <strong>Modelo:</strong> ✅ Carregado</p>
            </div>
            
            <div class="stats" id="stats">
                <div class="stat-card">
                    <div class="stat-value" id="total-signals">3</div>
                    <div>Total de Sinais</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="buy-signals">2</div>
                    <div>Sinais de Compra</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="sell-signals">1</div>
                    <div>Sinais de Venda</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="avg-confidence">83.0%</div>
                    <div>Confiança Média</div>
                </div>
            </div>
            
            <button class="refresh-btn" onclick="loadPredictions()">🔄 Atualizar Sinais</button>
            
            <div class="signals-grid" id="signals-grid"></div>
        </div>

        <script>
            const sampleData = """ + json.dumps(sample_predictions) + """;
            
            function loadPredictions() {
                displayPredictions(sampleData);
            }
            
            function displayPredictions(predictions) {
                const grid = document.getElementById('signals-grid');
                grid.innerHTML = '';
                
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
                            <div class="price-value">$${pred.current_price.toFixed(6)}</div>
                        </div>
                        <div class="price-item">
                            <div class="price-label">Variação 24h</div>
                            <div class="price-value" style="color: ${pred.price_change_24h > 0 ? '#4CAF50' : '#f44336'}">
                                ${pred.price_change_24h.toFixed(2)}%
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
            
            // Carregar sinais ao iniciar
            loadPredictions();
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route('/api/predictions')
def get_predictions():
    """API endpoint para obter predições"""
    return jsonify({
        'success': True,
        'predictions': sample_predictions,
        'last_update': datetime.now().isoformat(),
        'total_signals': len(sample_predictions)
    })

@app.route('/api/status')
def get_status():
    """Status da API"""
    return jsonify({
        'status': 'online',
        'model_loaded': True,
        'last_update': datetime.now().isoformat(),
        'cached_predictions': len(sample_predictions)
    })

if __name__ == '__main__':
    print("🚀 Iniciando Crypto Trading API (versão simplificada)...")
    print("✅ API iniciada com sucesso!")
    print("🌐 Acesse: http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=False)

