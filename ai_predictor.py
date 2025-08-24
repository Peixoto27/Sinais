# -*- coding: utf-8 -*-
import os, joblib

_MODEL = None
_MODEL_PATH = os.getenv("MODEL_FILE", "model.pkl")
_LOGGED_ACTIVE = False  # evita log duplicado por execução

def load_model():
    global _MODEL, _LOGGED_ACTIVE
    if _MODEL is not None:
        return _MODEL
    try:
        if os.path.exists(_MODEL_PATH):
            _MODEL = joblib.load(_MODEL_PATH)
        else:
            _MODEL = None
    except Exception as e:
        print(f"⚠️ IA: falha ao carregar modelo: {e}")
        _MODEL = None
    return _MODEL

def log_if_active(threshold: float):
    """Chame após load_model() no main para logar ativação uma única vez."""
    global _LOGGED_ACTIVE
    if _MODEL is not None and not _LOGGED_ACTIVE:
        print(f"🤖 IA treinada e agora ativa no cálculo de sinais! (limiar={int(threshold*100)}%)", flush=True)
        _LOGGED_ACTIVE = True

def predict_proba(model, X_row):
    try:
        if hasattr(model, "predict_proba"):
            return float(model.predict_proba([X_row])[0][1])
        pred = model.predict([X_row])[0]
        return float(pred)  # 0/1 em fallback
    except Exception as e:
        print(f"⚠️ IA: erro na predição: {e}")
        return None
