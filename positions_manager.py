# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime, timedelta

POSITIONS_FILE = os.getenv("POSITIONS_FILE", "positions.json")

# ---------- util ----------
def _now_utc():
    return datetime.utcnow()

def _load_positions():
    if not os.path.exists(POSITIONS_FILE):
        return {"open": [], "closed": []}
    try:
        with open(POSITIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"open": [], "closed": []}

def _save_positions(data):
    with open(POSITIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _pct_diff(a, b):
    try:
        a = float(a); b = float(b)
        if a == 0: return 999.0
        return abs(a - b) / abs(a) * 100.0
    except Exception:
        return 999.0

# ---------- API ----------
def should_send_and_register(sig: dict, cooldown_hours: float = 6.0, change_threshold_pct: float = 1.0):
    """
    Decide se envia um novo sinal para o mesmo símbolo.
    Regras:
      - Se não houver posição aberta do símbolo -> registra e envia.
      - Se houver:
          * se mudou (entry/tp/sl) mais que 'change_threshold_pct' -> atualiza e envia.
          * senão, se passou o cooldown_hours desde o último envio -> atualiza timestamp e envia.
          * caso contrário -> não envia (duplicado).
    Retorna: (bool ok_to_send, str reason)
    """
    symbol = sig.get("symbol")
    entry  = sig.get("entry")
    tp     = sig.get("tp")
    sl     = sig.get("sl")

    if not symbol:
        return False, "sem_symbol"

    book = _load_positions()
    open_list = book.get("open", [])
    now = _now_utc()

    # procura posição aberta do mesmo símbolo
    found = None
    for pos in open_list:
        if pos.get("symbol") == symbol and pos.get("status", "open") == "open":
            found = pos
            break

    if found is None:
        # registra nova posição
        open_list.append({
            "symbol": symbol,
            "entry": float(entry) if entry is not None else None,
            "tp": float(tp) if tp is not None else None,
            "sl": float(sl) if sl is not None else None,
            "created_at": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "last_sent_at": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "status": "open"
        })
        book["open"] = open_list
        _save_positions(book)
        return True, "novo"

    # já existe aberto -> checa mudança relevante
    changed = (
        _pct_diff(found.get("entry"), entry) > change_threshold_pct or
        _pct_diff(found.get("tp"), tp) > change_threshold_pct or
        _pct_diff(found.get("sl"), sl) > change_threshold_pct
    )

    # checa cooldown
    last_sent = found.get("last_sent_at")
    cooldown_ok = True
    if last_sent:
        try:
            last_dt = datetime.strptime(last_sent, "%Y-%m-%d %H:%M:%S UTC")
            cooldown_ok = (now - last_dt) >= timedelta(hours=float(cooldown_hours))
        except Exception:
            cooldown_ok = True  # se der erro de parse, deixa enviar

    if changed or cooldown_ok:
        # atualiza plano e timestamp; permite enviar
        if entry is not None: found["entry"] = float(entry)
        if tp is not None:    found["tp"]    = float(tp)
        if sl is not None:    found["sl"]    = float(sl)
        found["last_sent_at"] = now.strftime("%Y-%m-%d %H:%M:%S UTC")
        _save_positions(book)
        return True, ("mudou" if changed else "cooldown")

    # não envia duplicado
    return False, "duplicado"

def close_position(symbol: str, reason: str):
    """
    Fecha a posição do símbolo (move de open -> closed) com o motivo:
    'hit_tp' | 'hit_sl' | 'expirado'
    """
    book = _load_positions()
    open_list = book.get("open", [])
    new_open = []
    closed_flag = False
    now = _now_utc().strftime("%Y-%m-%d %H:%M:%S UTC")

    for pos in open_list:
        if pos.get("symbol") == symbol and pos.get("status", "open") == "open":
            pos["status"] = reason
            pos["closed_at"] = now
            closed = book.get("closed", [])
            closed.append(pos)
            book["closed"] = closed
            closed_flag = True
        else:
            new_open.append(pos)

    book["open"] = new_open
    _save_positions(book)
    return closed_flag
