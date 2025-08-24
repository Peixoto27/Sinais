import json
import os

TRADES_FILE = "open_trades.json"

def load_open_trades():
    """Carrega os trades abertos de um arquivo JSON."""
    if os.path.exists(TRADES_FILE):
        with open(TRADES_FILE, "r") as f:
            return json.load(f)
    return {}

def save_open_trades(trades):
    """Salva os trades abertos em um arquivo JSON."""
    with open(TRADES_FILE, "w") as f:
        json.dump(trades, f, indent=4)

def check_and_notify_closed_trades(open_trades, current_market_data, send_notification_func):
    """Verifica se trades abertos atingiram alvo ou stop loss e notifica."""
    closed_trades = []
    for symbol, trade_info in list(open_trades.items()): # Usar list() para permitir modificação durante iteração
        if symbol not in current_market_data or current_market_data[symbol].empty:
            print(f"⚠️ Dados atuais indisponíveis para {symbol} para monitoramento.")
            continue

        current_price = current_market_data[symbol]["close"].iloc[-1]
        entry_price = float(trade_info["entry_price"])
        target_price = float(trade_info["target_price"])
        stop_loss = float(trade_info["stop_loss"])

        message = None
        if current_price >= target_price: # Atingiu o alvo
            profit_percent = ((current_price - entry_price) / entry_price) * 100
            message = (
                f"✅ ALVO ATINGIDO para {symbol}!\n"
                f"💰 Entrada: {entry_price:.4f} | Alvo: {target_price:.4f} | Preço Atual: {current_price:.4f}\n"
                f"📈 Lucro: {profit_percent:.2f}%"
            )
            closed_trades.append(symbol)
        elif current_price <= stop_loss: # Atingiu o stop loss
            loss_percent = ((entry_price - current_price) / entry_price) * 100
            message = (
                f"❌ STOP LOSS ATINGIDO para {symbol}!\n"
                f"📉 Entrada: {entry_price:.4f} | Stop: {stop_loss:.4f} | Preço Atual: {current_price:.4f}\n"
                f"💔 Prejuízo: {loss_percent:.2f}%"
            )
            closed_trades.append(symbol)
        
        if message:
            print(f"[STATE_MANAGER] {message}")
            send_notification_func(message) # Envia a notificação

    for symbol in closed_trades:
        del open_trades[symbol] # Remove o trade fechado
    save_open_trades(open_trades) # Salva o estado atualizado

