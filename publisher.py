# -*- coding: utf-8 -*-
import json
from notifier_telegram import send_signal_notification

def publish_signal(sig: dict):
    # Deixa o notifier montar o texto (suporta os dois formatos)
    send_signal_notification(sig)

def publish_many(signals: list):
    for s in signals:
        publish_signal(s)
