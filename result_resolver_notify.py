# -*- coding: utf-8 -*-
import json, os
from datetime import datetime

from config import HISTORY_FILE, SIGNALS_FILE, SEND_STATUS_UPDATES
from coingecko_client import fetch_bulk_prices
from positions_manager import close_position
from notifier_telegram import send_signal_notification

# Tempo máximo do sinal “aberto” antes de expirar (pode por no .env como RESOLVE_EXPIRY_HOURS)
EXPIRY_HOURS = float(os.getenv("RESOLVE_EXPIRY_HOURS", "36"))

def _now_utc(): 
    return datetime.utcnow()

def _utc_from_ts(ts):
    try:
        return datetime.utcfromtimestamp(int(ts))
    except Exception:
        return None

def _load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def _save_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def _index_signals_by_symbol(signals):
    """Indexa últimos sinais aprovados por símbolo para fallback de entry/tp/sl."""
    idx = {}
    for s in signals:
        sym = s.get("symbol")
        if not sym:
            continue
        idx.setdefault(sym, []).append(s)
    for k in idx:
        idx[k].sort(key=lambda x: x.get("timestamp", 0), reverse=True)
    return idx

def main():
    print("🧮 Resolver+Notify: carregando…", flush=True)
    history = _load_json(HISTORY_FILE, [])
    signals = _load_json(SIGNALS_FILE, [])
    idx = _index_signals_by_symbol(signals)

    # Símbolos com registros pendentes (sem resultado ainda)
    pending_syms = set()
    for rec in history:
        if rec.get("result") in ("hit_tp", "hit_sl", "expirado"):
            continue
        sym = rec.get("symbol")
        if sym:
            pending_syms.add(sym)

    if not pending_syms:
        print("ℹ️ Nada pendente.", flush=True)
        return

    print(f"💱 Buscando preços de {len(pending_syms)} símbolos…", flush=True)
    prices = fetch_bulk_prices(list(pending_syms))
    now = _now_utc()
    updated = 0

    for rec in history:
        if rec.get("result") in ("hit_tp", "hit_sl", "expirado"):
            continue

        sym = rec.get("symbol")
        if not sym:
            continue

        # tenta obter entry/tp/sl do próprio histórico
        entry = rec.get("entry")
        tp    = rec.get("tp")
        sl    = rec.get("sl")

        # fallback: puxa do último sinal aprovado do mesmo símbolo
        if entry is None or tp is None or sl is None:
            last_list = idx.get(sym, [])
            if last_list:
                cand = last_list[0]
                entry = entry or cand.get("entry")
                tp    = tp    or cand.get("tp")
                sl    = sl    or cand.get("sl")

        if entry is None or tp is None or sl is None:
            # sem dados suficientes pra resolver
            continue

        pinfo = prices.get(sym)
        if not pinfo or "usd" not in pinfo:
            continue

        cur = float(pinfo["usd"])
        hit_tp = cur >= float(tp)
        hit_sl = cur <= float(sl)

        # expiração por tempo
        created = _utc_from_ts(rec.get("timestamp"))
        expired = False
        if created:
            age_h = (now - created).total_seconds() / 3600.0
            expired = age_h >= EXPIRY_HOURS

        if hit_tp or hit_sl or expired:
            rec["result"] = "hit_tp" if hit_tp else ("hit_sl" if hit_sl else "expirado")
            updated += 1

            # Fecha no positions.json (move de open -> closed)
            close_position(sym, rec["result"])

            # Notifica status se habilitado
            if SEND_STATUS_UPDATES:
                if hit_tp:
                    msg = f"✅ {sym}: Alvo (TP) atingido!"
                elif hit_sl:
                    msg = f"❌ {sym}: Stop (SL) acionado."
                else:
                    msg = f"⏳ {sym}: Sinal expirado após {int(EXPIRY_HOURS)}h."
                send_signal_notification(msg)

    if updated:
        _save_json(HISTORY_FILE, history)
        print(f"💾 Atualizados {updated} registros no {HISTORY_FILE}.", flush=True)
    else:
        print("ℹ️ Nenhuma atualização agora.", flush=True)

if __name__ == "__main__":
    main()
