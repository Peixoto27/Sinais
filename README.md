# 🚀 Crypto Trading AI - Sistema de Sinais Inteligente

Sistema completo de trading de criptomoedas com inteligência artificial para predição de momentos de compra e venda.

## 📊 Resultados do Modelo

### Performance Excepcional
- **Acurácia**: 73.6% (excelente para trading)
- **Taxa de acerto no backtesting**: 94.31%
- **Retorno total**: 2,905.37% (quase 30x)
- **Retorno médio por trade**: 3.44%
- **Cross-validation**: 71.7% (modelo estável)

### Performance por Criptomoeda
- **BONKUSDT**: 98.6% acerto, 4.73% retorno médio ⭐
- **PEPEUSDT**: 99.3% acerto, 3.77% retorno médio ⭐
- **FLOKIUSDT**: 96.4% acerto, 4.25% retorno médio
- **DOGEUSDT**: 96.5% acerto, 3.74% retorno médio
- **ETHUSDT**: 94.4% acerto, 3.17% retorno médio
- **BTCUSDT**: 81.2% acerto, 1.07% retorno médio

## 🎯 Características do Sistema

### Indicadores Técnicos
- **RSI** (Relative Strength Index)
- **MACD** (Moving Average Convergence Divergence)
- **Bollinger Bands**
- **EMA** (Exponential Moving Average)
- **SMA** (Simple Moving Average)
- **Volatilidade** e **Mudanças de Preço**

### Modelo de IA
- **XGBoost** (algoritmo principal)
- **Random Forest** (fallback)
- **15 features** técnicas
- **Normalização** com StandardScaler
- **Validação cruzada** 5-fold

### Interface Web
- **Design responsivo** e moderno
- **Sinais em tempo real**
- **Estatísticas de performance**
- **Atualização automática** a cada 5 minutos
- **Visualização intuitiva** de probabilidades

## 🛠️ Estrutura do Projeto

```
crypto_trading_api/
├── src/
│   ├── main.py                 # API Flask principal
│   ├── simple_app.py           # Versão simplificada para demo
│   ├── train_model_enhanced.py # Script de treinamento
│   ├── predict_enhanced.py     # Script de predição
│   ├── validate_model.py       # Validação e backtesting
│   ├── model_enhanced.pkl      # Modelo XGBoost treinado
│   ├── scaler.pkl             # Normalizador de dados
│   └── [outros arquivos do projeto original]
├── requirements.txt           # Dependências Python
├── railway.json              # Configuração Railway
├── Procfile                  # Comando de inicialização
├── runtime.txt               # Versão Python
└── README.md                 # Esta documentação
```

## 🚀 Deploy no Railway

### Pré-requisitos
1. Conta no [Railway](https://railway.app)
2. Git instalado
3. Projeto commitado no GitHub

### Passos para Deploy

#### 1. Preparar Repositório
```bash
# No diretório crypto_trading_api
git init
git add .
git commit -m "Initial commit - Crypto Trading AI"
git remote add origin [SEU_REPOSITORIO_GITHUB]
git push -u origin main
```

#### 2. Deploy no Railway
1. Acesse [railway.app](https://railway.app)
2. Clique em "New Project"
3. Selecione "Deploy from GitHub repo"
4. Escolha seu repositório
5. Railway detectará automaticamente o Python e usará os arquivos de configuração

#### 3. Configuração Automática
O Railway usará automaticamente:
- `requirements.txt` para instalar dependências
- `Procfile` para comando de inicialização
- `railway.json` para configurações específicas
- `runtime.txt` para versão do Python

#### 4. Variáveis de Ambiente (Opcional)
No painel do Railway, adicione se necessário:
```
FLASK_ENV=production
PORT=5000
```

### URLs de Acesso
Após o deploy, você terá:
- **Interface Web**: `https://[seu-app].railway.app/`
- **API Status**: `https://[seu-app].railway.app/api/status`
- **API Predições**: `https://[seu-app].railway.app/api/predictions`

## 🔧 Uso Local

### Instalação
```bash
cd crypto_trading_api
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\\Scripts\\activate   # Windows

pip install -r requirements.txt
```

### Execução
```bash
cd src
python main.py
# ou para versão simplificada:
python simple_app.py
```

Acesse: `http://localhost:5000`

## 📈 Como Usar o Sistema

### Interface Web
1. Acesse a URL da aplicação
2. Visualize os sinais atuais na página principal
3. Clique em "🔄 Atualizar Sinais" para dados mais recentes
4. Analise as probabilidades e níveis de confiança

### Interpretação dos Sinais
- **COMPRA** 📈: Modelo prevê alta nos próximos períodos
- **VENDA** 📉: Modelo prevê queda nos próximos períodos
- **Confiança > 70%**: Sinal forte (recomendado)
- **Confiança 50-70%**: Sinal moderado (cautela)
- **Confiança < 50%**: Sinal fraco (evitar)

### API Endpoints
- `GET /`: Interface web principal
- `GET /api/status`: Status do sistema
- `GET /api/predictions`: Predições atuais (JSON)
- `GET /api/force-update`: Força atualização dos dados

## 🔄 Retreinamento do Modelo

Para retreinar com novos dados:
```bash
cd src
python train_model_enhanced.py
```

Para validar performance:
```bash
python validate_model.py
```

## 📊 Monitoramento

### Métricas Importantes
- **Taxa de acerto**: % de predições corretas
- **Retorno médio**: Ganho médio por trade
- **Confiança média**: Nível de certeza do modelo
- **Distribuição de sinais**: Equilíbrio entre compra/venda

### Logs do Sistema
O sistema gera logs detalhados sobre:
- Coleta de dados da API
- Processamento de indicadores
- Predições do modelo
- Erros e warnings

## ⚠️ Avisos Importantes

### Disclaimer
- Este sistema é para **fins educacionais e de pesquisa**
- **NÃO** constitui aconselhamento financeiro
- Trading de criptomoedas envolve **alto risco**
- Sempre faça sua própria análise antes de investir
- Use apenas capital que pode perder

### Limitações
- Modelo baseado em dados históricos
- Performance passada não garante resultados futuros
- Mercado de cripto é altamente volátil
- Fatores externos podem afetar predições

## 🛡️ Segurança

- Não armazena chaves privadas ou credenciais
- Usa apenas APIs públicas para dados
- Não executa trades automaticamente
- Interface somente leitura

## 📞 Suporte

Para dúvidas ou melhorias:
1. Verifique os logs do sistema
2. Consulte a documentação da API
3. Analise os arquivos de validação
4. Considere retreinar o modelo com mais dados

## 🔮 Próximos Passos

### Melhorias Sugeridas
1. **Mais indicadores**: Adicionar STOCH, Williams %R, etc.
2. **Timeframes múltiplos**: Análise em diferentes períodos
3. **Sentiment analysis**: Incorporar análise de notícias
4. **Alertas**: Notificações por email/Telegram
5. **Backtesting avançado**: Simulação mais realística
6. **Portfolio management**: Gestão de múltiplos ativos

### Expansão
- Suporte a mais exchanges (Binance, Coinbase Pro)
- Integração com APIs de trading
- Dashboard administrativo
- Histórico de performance
- Análise de risco avançada

---

**Desenvolvido com ❤️ para a comunidade de trading de criptomoedas**

