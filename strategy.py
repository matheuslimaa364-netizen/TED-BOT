import numpy as np
import pandas as pd


def generate_demo_candles(timeframe="M5", periods=80, seed=None):
    """Gera candles sintéticos para testar a estratégia; não usa preços reais."""
    rng = np.random.default_rng(seed)
    drift = rng.choice([-0.00025, 0.00025])
    returns = rng.normal(loc=drift, scale=0.0012, size=periods)
    close = 1.1000 * np.exp(np.cumsum(returns))
    open = np.concatenate([[close[0] * (1 - returns[0])], close[:-1]])
    wick_up = rng.uniform(0.0001, 0.0010, size=periods)
    wick_down = rng.uniform(0.0001, 0.0010, size=periods)
    high = np.maximum(open, close) + wick_up
    low = np.minimum(open, close) - wick_down
    if timeframe == "M1":
        freq = "min"
    elif timeframe == "M15":
        freq = "15min"
    else:
        freq = "5min"

    times = pd.date_range(end=pd.Timestamp.now(), periods=periods, freq=freq)
    return pd.DataFrame({"time": times, "open": open, "high": high, "low": low, "close": close})

def analyze_market(candles):
    """Análise educativa simples: tendência, candle e proximidade de Fibonacci."""
    if candles is None or len(candles) < 25:
        return {
            "signal": "AGUARDAR", "trend": "Indefinida", "last_price": 0.0,
            "confidence": "Baixa", "reason": "Dados insuficientes para analisar.",
            "fibonacci": {"38.2%": 0.0, "50.0%": 0.0, "61.8%": 0.0}
        }

    df = candles.copy().reset_index(drop=True)
    closes = df["close"]
    last = df.iloc[-1]
    prev = df.iloc[-2]
    sma_fast = closes.rolling(8).mean().iloc[-1]
    sma_slow = closes.rolling(21).mean().iloc[-1]
    trend = "Alta" if sma_fast > sma_slow else "Baixa" if sma_fast < sma_slow else "Lateral"

    body = abs(last["close"] - last["open"])
    candle_range = max(last["high"] - last["low"], 1e-9)
    lower_wick = min(last["open"], last["close"]) - last["low"]
    upper_wick = last["high"] - max(last["open"], last["close"])
    bullish_engulf = (
        last["close"] > last["open"] and prev["close"] < prev["open"]
        and last["close"] >= prev["open"] and last["open"] <= prev["close"]
    )
    bearish_engulf = (
        last["close"] < last["open"] and prev["close"] > prev["open"]
        and last["open"] >= prev["close"] and last["close"] <= prev["open"]
    )
    bullish_rejection = lower_wick / candle_range > 0.45 and last["close"] > last["open"]
    bearish_rejection = upper_wick / candle_range > 0.45 and last["close"] < last["open"]

    swing_high = float(df["high"].tail(30).max())
    swing_low = float(df["low"].tail(30).min())
    span = max(swing_high - swing_low, 1e-9)
    # Retracement levels measured downward from the recent high.
    fibs = {
        "38.2%": swing_high - span * 0.382,
        "50.0%": swing_high - span * 0.500,
        "61.8%": swing_high - span * 0.618,
    }
    price = float(last["close"])
    near_fib = min(abs(price - level) / max(span, 1e-9) for level in fibs.values()) < 0.12

    sinal = "AGUARDAR"
    confianca = "Baixa"
    razao = "Os critérios ainda não coincidem."
    padrao_alta = engolfo_de_alta or rejeicao_otimista
    padrao_baixa = engolfo_de_baixa or rejeicao_baixista

    if tendencia == "Alta" and padrao_alta and proximo_de_Fibonacci:
        sinal = "COMPRA (simulada)"
        confianca = "Alta"
        padrao = "engolfo de alta" if engolfo_de_alta else "rejeição compradora"
        razao = f"Tendência de alta + {padrao} + proximidade de Fibonacci."

    elif tendencia == "Baixa" and padrao_baixa and proximo_de_Fibonacci:
        sinal = "VENDA (simulada)"
        confianca = "Alta"
        padrao = "engolfo de baixa" if engolfo_de_baixa else "rejeição vendedora"
        razao = f"Tendência de baixa + {padrao} + proximidade de Fibonacci."

    else:
        detalhes = []
        detalhes.append(f"tendência: {tendencia.lower()}")
        detalhes.append("padrão de candle identificado" if (padrao_alta or padrao_baixa) else "sem padrão claro")
        detalhes.append("próximo de Fibonacci" if proximo_de_Fibonacci else "longe das zonas de Fibonacci")
        razao = "AGUARDAR: " + "; ".join(detalhes) + "."

    return {
        "signal": signal,
        "trend": trend,
        "last_price": price,
        "confidence": confidence,
        "reason": reason,
        "fibonacci": fibs,
    }
