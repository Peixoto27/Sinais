# -*- coding: utf-8 -*-
import json
import os
import time
from datetime import datetime

HISTORY_FILE = "history.json"

def load_history():
    """Carrega histórico salvo do arquivo"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("⚠️ Erro ao ler history.json, recriando arquivo.")
            return []
    return []

def save_history(data):
    """Salva lista de sinais no arquivo"""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def append_to_history(signal_data):
    """
    Adiciona um novo registro ao histórico.
    signal_data deve conter:
      - symbol
      - timestamp
      - indicadores (RSI, MACD, EMA20, EMA50, BB_up, BB_mid, BB_low)
      - score
      - decisão (enviado ou não)
      - resultado (tp/hit_stop/pendente) — inicialmente 'pendente'
    """
    history = load_history()
    signal_data["recorded_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    signal_data["result"] = "pendente"  # vamos atualizar depois
    history.append(signal_data)
    save_history(history)
    print(f"💾 Histórico atualizado ({len(history)} registros).")
