# -*- coding: utf-8 -*-
"""
Script de treinamento melhorado para modelo de ML de trading de criptomoedas
Usa os dados históricos coletados para treinar um modelo preditivo
"""
import os, json, joblib, numpy as np, pandas as pd
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Importar funções do projeto
from indicators import rsi, macd, ema, bollinger
from apply_strategies import score_signal

# Configurações
DATA_RAW_FILE = "data_raw.json"
MODEL_FILE = "model_enhanced.pkl"
SCALER_FILE = "scaler.pkl"
MIN_SAMPLES = 50  # Reduzido para permitir treinamento com dados atuais

def load_raw_data():
    """Carrega dados brutos do arquivo JSON"""
    if not os.path.exists(DATA_RAW_FILE):
        raise FileNotFoundError(f"{DATA_RAW_FILE} não encontrado.")
    
    with open(DATA_RAW_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def calculate_technical_indicators(ohlc_data):
    """Calcula indicadores técnicos a partir dos dados OHLC"""
    if len(ohlc_data) < 60:
        return None
    
    # Extrair preços de fechamento
    closes = [candle['close'] for candle in ohlc_data]
    highs = [candle['high'] for candle in ohlc_data]
    lows = [candle['low'] for candle in ohlc_data]
    volumes = [candle.get('volume', 1000) for candle in ohlc_data]  # Volume padrão se não disponível
    
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
    
    return {
        'rsi': rsi_values,
        'macd_line': macd_line,
        'signal_line': signal_line,
        'histogram': histogram,
        'ema20': ema20,
        'ema50': ema50,
        'bb_upper': bb_upper,
        'bb_middle': bb_middle,
        'bb_lower': bb_lower,
        'sma10': sma10,
        'price_change': price_change,
        'volatility': volatility,
        'closes': closes,
        'highs': highs,
        'lows': lows
    }

def create_features_and_targets(raw_data):
    """Cria features e targets para treinamento"""
    X, y, symbols = [], [], []
    
    for asset_data in raw_data:
        symbol = asset_data['symbol']
        ohlc = asset_data['ohlc']
        
        indicators = calculate_technical_indicators(ohlc)
        if indicators is None:
            continue
        
        # Criar features para cada ponto temporal (últimos 30 pontos)
        for i in range(30, len(indicators['closes'])):
            features = []
            
            # Indicadores técnicos atuais
            if (indicators['rsi'][i] is not None and 
                indicators['macd_line'][i] is not None and
                indicators['ema20'][i] is not None and
                indicators['bb_upper'][i] is not None):
                
                features.extend([
                    indicators['rsi'][i],
                    indicators['macd_line'][i],
                    indicators['signal_line'][i] if indicators['signal_line'][i] is not None else 0,
                    indicators['histogram'][i] if indicators['histogram'][i] is not None else 0,
                    indicators['ema20'][i],
                    indicators['ema50'][i] if indicators['ema50'][i] is not None else indicators['ema20'][i],
                    indicators['bb_upper'][i],
                    indicators['bb_middle'][i],
                    indicators['bb_lower'][i],
                    indicators['sma10'][i] if indicators['sma10'][i] is not None else indicators['closes'][i],
                    indicators['price_change'][i],
                    indicators['volatility'][i] if indicators['volatility'][i] is not None else 0,
                ])
                
                # Features de contexto de mercado
                current_price = indicators['closes'][i]
                features.extend([
                    current_price / indicators['ema20'][i] - 1,  # Distância da EMA20
                    current_price / indicators['bb_middle'][i] - 1,  # Posição nas Bollinger Bands
                    (indicators['bb_upper'][i] - indicators['bb_lower'][i]) / indicators['bb_middle'][i],  # Largura das BB
                ])
                
                # Target: movimento futuro (próximos 5 períodos)
                future_prices = indicators['closes'][i+1:i+6] if i+5 < len(indicators['closes']) else []
                if len(future_prices) >= 3:
                    future_return = (max(future_prices) - current_price) / current_price
                    target = 1 if future_return > 0.02 else 0  # 2% de ganho mínimo
                    
                    X.append(features)
                    y.append(target)
                    symbols.append(symbol)
    
    return np.array(X), np.array(y), symbols

def train_model(X, y):
    """Treina o modelo de machine learning"""
    print(f"📊 Treinando com {len(X)} amostras...")
    
    # Dividir dados
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Normalizar features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Tentar XGBoost primeiro, depois Random Forest
    try:
        from xgboost import XGBClassifier
        model = XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric='logloss'
        )
        print("🚀 Usando XGBoost")
    except ImportError:
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        print("🌲 Usando Random Forest")
    
    # Treinar modelo
    model.fit(X_train_scaled, y_train)
    
    # Avaliar modelo
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"✅ Acurácia: {accuracy:.3f}")
    print(f"📈 Distribuição de classes - Treino: {np.bincount(y_train)}")
    print(f"📈 Distribuição de classes - Teste: {np.bincount(y_test)}")
    
    # Cross-validation
    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
    print(f"🔄 Cross-validation: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
    
    # Relatório detalhado
    print("\n📋 Relatório de classificação:")
    print(classification_report(y_test, y_pred))
    
    return model, scaler, accuracy

def main():
    print("🧠 Iniciando treinamento do modelo de IA para trading...")
    
    # Carregar dados
    try:
        raw_data = load_raw_data()
        print(f"📁 Carregados dados de {len(raw_data)} ativos")
    except FileNotFoundError as e:
        print(f"❌ Erro: {e}")
        return
    
    # Criar features e targets
    X, y, symbols = create_features_and_targets(raw_data)
    
    if len(X) < MIN_SAMPLES:
        print(f"⚠️ Poucos dados para treinamento: {len(X)} < {MIN_SAMPLES}")
        print("💡 Execute o main.py algumas vezes para coletar mais dados históricos")
        return
    
    print(f"🔢 Features criadas: {X.shape}")
    print(f"🎯 Distribuição de targets: {np.bincount(y)}")
    
    # Treinar modelo
    model, scaler, accuracy = train_model(X, y)
    
    # Salvar modelo e scaler
    joblib.dump(model, MODEL_FILE)
    joblib.dump(scaler, SCALER_FILE)
    
    print(f"💾 Modelo salvo em {MODEL_FILE}")
    print(f"💾 Scaler salvo em {SCALER_FILE}")
    print(f"🕒 Treinamento concluído: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return model, scaler, accuracy

if __name__ == "__main__":
    main()

