# -*- coding: utf-8 -*-
import os, json, joblib, numpy as np
from datetime import datetime
from config import HISTORY_FILE, MODEL_FILE

MIN_SAMPLES = int(os.getenv("AI_MIN_SAMPLES", "200"))  # mínimo para treinar
FEATURES = ["RSI","MACD_line","Signal_line","Hist","EMA20","EMA50","BB_up","BB_mid","BB_low","score"]

def load_history(path):
    if not os.path.exists(path): return []
    try:
        with open(path, "r", encoding="utf-8") as f: return json.load(f)
    except Exception: return []

def build_dataset(history):
    X, y = [], []
    for rec in history:
        if rec.get("result") not in ("hit_tp","hit_sl"):  # só rotulados
            continue
        ind = rec.get("indicators") or {}
        sc = rec.get("score")
        row = []
        ok = True
        for k in FEATURES:
            val = sc if k == "score" else ind.get(k)
            if val is None: ok = False; break
            row.append(float(val))
        if not ok: continue
        X.append(row)
        y.append(1 if rec["result"] == "hit_tp" else 0)
    return np.array(X, float), np.array(y, int)

def train_and_save(X, y, path):
    # tenta XGBoost, senão cai pra GradientBoosting
    try:
        from xgboost import XGBClassifier
        model = XGBClassifier(
            n_estimators=300, max_depth=5, learning_rate=0.05,
            subsample=0.9, colsample_bytree=0.9, eval_metric="logloss",
            n_jobs=2, random_state=42
        )
    except Exception:
        from sklearn.ensemble import GradientBoostingClassifier
        model = GradientBoostingClassifier(random_state=42)
    model.fit(X, y)
    joblib.dump(model, path)
    return model

def main():
    print("🧠 Treino IA: carregando histórico…", flush=True)
    hist = load_history(HISTORY_FILE)
    X, y = build_dataset(hist)
    n = len(y)
    print(f"📊 Amostras rotuladas: {n}", flush=True)

    if n < MIN_SAMPLES:
        print(f"⏸️ Poucos dados ({n} < {MIN_SAMPLES}). Treino adiado.", flush=True)
        return

    first_time = not os.path.exists(MODEL_FILE)
    model = train_and_save(X, y, MODEL_FILE)

    if first_time:
        print("📚 IA concluída: modelo inicial pronto para uso nos próximos sinais.", flush=True)
    else:
        print("🔁 IA re-treinada e atualizada com histórico recente.", flush=True)

    print(f"✅ Modelo salvo em {MODEL_FILE} ({datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC)", flush=True)

if __name__ == "__main__":
    main()
