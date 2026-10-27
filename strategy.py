import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_demo_candles(n=80, seed=None):
    rng = np.random.default_rng(seed)
    changes = rng.normal(0.02, 0.45, n)
    close = 100 + np.cumsum(changes)
    open_ = np.r_[close[0], close[:-1] + rng.normal(0, 0.12, n-1)]
    high = np.maximum(open_, close) + rng.uniform(0.05, 0.4, n)
    low = np.minimum(open_, close) - rng.uniform(0.05, 0.4, n)
    times = [(datetime.now() - timedelta(minutes=5*(n-i))).strftime("%H:%M") for i in range(n)]
    return pd.DataFrame({"Hora": times, "Abertura": open_, "Máxima": high, "Mínima": low, "Fechamento": close})

def analyze_market(df):
    if len(df) < 20:
        return {
            "direcao": "Indefinida", "estrutura": "Dados insuficientes",
            "padrao": "Nenhum", "fib_regiao": "Indisponível",
            "sinal": "AGUARDAR", "motivo": "Aguardando mais candles"
        }

    close = df["Fechamento"]
    high = df["Máxima"]
    low = df["Mínima"]
    recent = close.iloc[-10:]
    slope = recent.iloc[-1] - recent.iloc[0]

    if slope > 0.35:
        direction = "Altista"
        structure = "Possível sequência de fundos/topos ascendentes"
    elif slope < -0.35:
        direction = "Baixista"
        structure = "Possível sequência de topos/fundos descendentes"
    else:
        direction = "Lateral / indefinida"
        structure = "Sem direção clara"

    # Fibonacci on the recent swing range. Illustrative heuristic only.
    swing_high = float(high.iloc[-20:].max())
    swing_low = float(low.iloc[-20:].min())
    span = max(swing_high - swing_low, 1e-9)
    current = float(close.iloc[-1])
    if direction == "Altista":
        fib_382 = swing_high - span * 0.382
        fib_500 = swing_high - span * 0.500
        fib_618 = swing_high - span * 0.618
        distance = min(abs(current-fib_382), abs(current-fib_500), abs(current-fib_618))
        region = "Próxima de 38,2%" if abs(current-fib_382) == distance else ("Próxima de 50%" if abs(current-fib_500) == distance else "Próxima de 61,8%")
    else:
        fib_382 = swing_low + span * 0.382
        fib_500 = swing_low + span * 0.500
        fib_618 = swing_low + span * 0.618
        distance = min(abs(current-fib_382), abs(current-fib_500), abs(current-fib_618))
        region = "Próxima de 38,2%" if abs(current-fib_382) == distance else ("Próxima de 50%" if abs(current-fib_500) == distance else "Próxima de 61,8%")

    o = float(df["Abertura"].iloc[-1])
    c = float(df["Fechamento"].iloc[-1])
    h = float(df["Máxima"].iloc[-1])
    l = float(df["Mínima"].iloc[-1])
    body = abs(c-o)
    upper_wick = h-max(o,c)
    lower_wick = min(o,c)-l

    if lower_wick > body*1.8 and c > o:
        pattern = "Possível rejeição compradora"
    elif upper_wick > body*1.8 and c < o:
        pattern = "Possível rejeição vendedora"
    else:
        pattern = "Sem padrão de rejeição claro"

    # Conservative educational signal: direction + candle rejection.
    signal = "AGUARDAR"
    reason = "Não há confluência suficiente; aguardar."
    if direction == "Altista" and "compradora" in pattern and ("50%" in region or "61,8%" in region):
        signal = "COMPRA (DEMO)"
        reason = "Tendência estimada altista + possível rejeição + região de retração."
    elif direction == "Baixista" and "vendedora" in pattern and ("50%" in region or "61,8%" in region):
        signal = "VENDA (DEMO)"
        reason = "Tendência estimada baixista + possível rejeição + região de retração."

    return {
        "direcao": direction,
        "estrutura": structure,
        "padrao": pattern,
        "fib_regiao": region,
        "sinal": signal,
        "motivo": reason
    }
