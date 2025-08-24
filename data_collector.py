# data_collector.py
import ccxt
import pandas as pd
from datetime import datetime

def collect_historical_data(symbol, timeframe='1h', years=2):
    """
    Coleta uma grande quantidade de dados históricos e salva em um arquivo CSV.
    """
    print(f"Iniciando coleta de dados históricos para {symbol}...")
    exchange = ccxt.binance()
    
    # Calcula o timestamp de início (anos atrás)
    since = exchange.parse8601(datetime.now().strftime('%Y-%m-%dT00:00:00Z')) - (years * 365 * 24 * 60 * 60 * 1000)
    
    all_ohlcv = []
    
    try:
        while since < exchange.milliseconds():
            print(f"Buscando dados a partir de {exchange.iso8601(since)}...")
            # O CCXT busca em lotes, geralmente de 500 a 1000 velas
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since)
            if len(ohlcv):
                since = ohlcv[-1][0] + 1 # Move o 'since' para depois da última vela recebida
                all_ohlcv.extend(ohlcv)
            else:
                break # Sai do loop se não houver mais dados
    except Exception as e:
        print(f"Erro durante a coleta de dados: {e}")

    if not all_ohlcv:
        print("Nenhum dado foi coletado.")
        return

    # Converte para DataFrame do Pandas
    df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    # Salva em um arquivo CSV
    filename = f"historical_data_{symbol.replace('/', '_')}_{timeframe}.csv"
    df.to_csv(filename, index=False)
    
    print(f"✅ Sucesso! {len(df)} registros salvos em '{filename}'.")

# --- Para executar este script ---
if __name__ == "__main__":
    # Vamos começar coletando dados para o Bitcoin
    # Este processo pode demorar alguns minutos!
    collect_historical_data('BTC/USDT', timeframe='1h', years=2)

