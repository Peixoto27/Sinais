# -*- coding: utf-8 -*-
import requests, time

# Bot/Canal
BOT_TOKEN = "7360602779:AAFIpncv7fkXaEX5PdWdEAUBb7NQ9SeA-F0"
CHAT_ID   = "-1002705937565"   # id numérico do canal

def _post(url, payload, max_retries=3, retry_delay=2):
    for attempt in range(max_retries):
        try:
            r = requests.post(url, json=payload, timeout=12)
            print(f"[TG] tentativa {attempt+1}, status={r.status_code}, resp={r.text[:200]}")
            if r.status_code == 200 and r.json().get("ok"):
                return True
            if r.status_code == 429:
                ra = r.json().get("parameters", {}).get("retry_after", retry_delay)
                time.sleep(float(ra))
            else:
                time.sleep(retry_delay); retry_delay *= 2
        except requests.RequestException as e:
            print(f"[TG] erro req: {e}")
            time.sleep(retry_delay); retry_delay *= 2
    return False

def _build_text_html(content: dict) -> str:
    symbol = content.get("symbol","N/A")
    entry  = content.get("entry_price", content.get("entry"))
    tp     = content.get("target_price", content.get("tp"))
    sl     = content.get("stop_loss", content.get("sl"))
    rr     = content.get("risk_reward")
    conf   = content.get("confidence_score", content.get("confidence"))
    if isinstance(conf, float) and conf <= 1: conf = round(conf*100,2)
    strat  = content.get("strategy","RSI+MACD+EMA+BB")
    created= content.get("created_at", content.get("timestamp"))
    sig_id = content.get("id","")
    ai     = bool(content.get("ai", False))
    ai_pb  = content.get("ai_proba")

    header = "🧠 <b>IA ATIVA</b> — " if ai else ""
    lines = [
        f"{header}📢 <b>Novo sinal</b> para <b>{symbol}</b>",
        f"🎯 <b>Entrada:</b> <code>{entry}</code>",
        f"🎯 <b>Alvo:</b>   <code>{tp}</code>",
        f"🛑 <b>Stop:</b>   <code>{sl}</code>",
    ]
    if rr is not None:     lines.append(f"📊 <b>R:R:</b> <code>{rr}</code>")
    if conf is not None:   lines.append(f"📈 <b>Confiança:</b> <code>{conf}%</code>")
    if ai_pb is not None:  lines.append(f"🧠 <b>IA (proba):</b> <code>{ai_pb}%</code>")
    lines.append(f"🧠 <b>Estratégia:</b> <code>{strat}</code>")
    if created is not None:lines.append(f"📅 <b>Criado:</b> <code>{created}</code>")
    if sig_id:             lines.append(f"🆔 <b>ID:</b> <code>{sig_id}</code>")
    return "\n".join(lines)

def send_signal_notification(content, max_retries=3, retry_delay=2):
    try:
        text = _build_text_html(content) if isinstance(content, dict) else str(content)
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
        ok = _post(url, payload, max_retries=max_retries, retry_delay=retry_delay)
        print("✅ Notificação enviada." if ok else "❌ Falha no envio após retries.")
        return ok
    except Exception as e:
        print(f"❌ Erro crítico notifier: {e}")
        return False
