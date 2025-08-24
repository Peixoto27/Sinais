# news_fetcher.py (Versão com NewsAPI)
import requests
import os
from datetime import datetime, timedelta

# URL base da NewsAPI
NEWS_API_URL = "https://newsapi.org/v2/everything"

def get_recent_news(symbol):
    """Busca as notícias mais recentes para um símbolo usando a NewsAPI."""
    
    # Pega a chave de API das variáveis de ambiente
    api_key = os.getenv("NEWS_API_KEY")
    
    if not api_key:
        print("⚠️ Chave da NewsAPI não encontrada. Pulando análise de sentimento.")
        return []

    # Formata o termo de busca (ex: 'BTCUSDT' -> 'Bitcoin OR BTC')
    currency_name = symbol.replace("USDT", "").lower()
    currency_code = symbol.replace("USDT", "")
    query = f'"{currency_name}" OR "{currency_code}"'
    
    # Busca notícias das últimas 24 horas para manter a relevância
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S')

    params = {
        'q': query,
        'apiKey': api_key,
        'language': 'en',       # Busca notícias em inglês para melhor análise de sentimento
        'sortBy': 'relevancy',  # Prioriza as notícias mais relevantes
        'from': yesterday,
        'pageSize': 20          # Pega até 20 notícias para analisar
    }
    
    try:
        response = requests.get(NEWS_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') == 'ok' and data.get('articles'):
            # Retorna uma lista dos títulos dos artigos
            return [article['title'] for article in data['articles']]
        else:
            # Imprime o erro se a API retornar um status de falha
            if data.get('status') == 'error':
                print(f"⚠️ Erro da NewsAPI para {symbol}: {data.get('message')}")
            return []
        
    except Exception as e:
        print(f"❌ Erro crítico ao buscar notícias para {symbol}: {e}")
        return []
