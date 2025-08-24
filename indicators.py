# -*- coding: utf-8 -*-
from typing import List

def ema(series: List[float], period: int):
    k = 2 / (period + 1)
    ema_vals = []
    prev = None
    for price in series:
        prev = price if prev is None else price * k + prev * (1 - k)
        ema_vals.append(prev)
    return ema_vals

def rsi(series: List[float], period: int = 14):
    if len(series) < period + 1:
        return [None] * len(series)
    gains, losses = [], []
    for i in range(1, len(series)):
        ch = series[i] - series[i-1]
        gains.append(max(ch, 0))
        losses.append(max(-ch, 0))
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    rsis = [None]*(period)
    for i in range(period, len(series)-1):
        gain = gains[i-1]; loss = losses[i-1]
        avg_gain = (avg_gain*(period-1) + gain) / period
        avg_loss = (avg_loss*(period-1) + loss) / period
        if avg_loss == 0:
            rsi_val = 100
        else:
            rs = avg_gain / avg_loss
            rsi_val = 100 - (100/(1+rs))
        rsis.append(rsi_val)
    while len(rsis) < len(series):
        rsis.append(rsis[-1] if rsis[-1] is not None else 50.0)
    return rsis

def macd(series: List[float], fast=12, slow=26, signal=9):
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = [f - s for f, s in zip(ema_fast, ema_slow)]
    signal_line = ema(macd_line, signal)
    hist = [m - s for m, s in zip(macd_line, signal_line)]
    return macd_line, signal_line, hist

def bollinger(series: List[float], period=20, mult=2.0):
    if len(series) < period:
        n = len(series)
        return [None]*n, [None]*n, [None]*n
    sma, stds = [], []
    from math import sqrt
    for i in range(len(series)):
        if i < period-1:
            sma.append(None); stds.append(None)
        else:
            window = series[i-period+1:i+1]
            m = sum(window)/period
            sma.append(m)
            var = sum((x-m)**2 for x in window)/period
            stds.append(sqrt(var))
    upper = [ (m + mult*s) if m is not None and s is not None else None for m,s in zip(sma,stds) ]
    lower = [ (m - mult*s) if m is not None and s is not None else None for m,s in zip(sma,stds) ]
    return upper, sma, lower
