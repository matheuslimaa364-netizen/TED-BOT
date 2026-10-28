import numpy as np
import pandas as pd


# =========================================================
# GERADOR DE CANDLES SINTÉTICOS
# =========================================================

def generate_demo_candles(
    timeframe="M5",
    periods=100,
    seed=None,
    start_price=1.1000
):
    """
    Gera candles sintéticos somente para estudo e simulação.
    Não utiliza preços reais.
    """

    rng = np.random.default_rng(seed)

    # Pequena tendência aleatória
    drift = rng.choice([
        -0.00025,
        -0.00015,
        0.0,
        0.00015,
        0.00025
    ])

    # Movimento dos preços
    returns = rng.normal(
        loc=drift,
        scale=0.0012,
        size=periods
    )

    close = start_price * np.exp(
        np.cumsum(returns)
    )

    open_ = np.concatenate(
        ([start_price], close[:-1])
    )

    wick_up = rng.uniform(
        0.0001,
        0.0010,
        size=periods
    )

    wick_down = rng.uniform(
        0.0001,
        0.0010,
        size=periods
    )

    high = np.maximum(
        open_,
        close
    ) + wick_up

    low = np.minimum(
        open_,
        close
    ) - wick_down

    # Frequência do gráfico
    if timeframe == "M1":
        freq = "1min"

    elif timeframe == "M15":
        freq = "15min"

    else:
        freq = "5min"

    times = pd.date_range(
        end=pd.Timestamp.now(),
        periods=periods,
        freq=freq
    )

    return pd.DataFrame({
        "time": times,
        "open": open_,
        "high": high,
        "low": low,
        "close": close
    })


# =========================================================
# ANÁLISE DE MERCADO
# =========================================================

def analyze_market(candles):
    """
    Estratégia educacional:
    tendência + Price Action + Fibonacci.
    """

    # -----------------------------------------------------
    # SEGURANÇA
    # -----------------------------------------------------

    if candles is None or len(candles) < 30:

        return {
            "signal": "AGUARDAR",
            "trend": "Indefinida",
            "last_price": 0.0,
            "confidence": "Baixa",
            "reason": "Dados insuficientes para análise.",
            "fibonacci": {
                "38.2%": 0.0,
                "50.0%": 0.0,
                "61.8%": 0.0
            }
        }

    df = candles.copy().reset_index(drop=True)

    closes = df["close"]

    last = df.iloc[-1]
    prev = df.iloc[-2]


    # =====================================================
    # TENDÊNCIA
    # =====================================================

    sma_fast = closes.rolling(8).mean().iloc[-1]
    sma_slow = closes.rolling(21).mean().iloc[-1]

    if sma_fast > sma_slow:
        trend = "Alta"

    elif sma_fast < sma_slow:
        trend = "Baixa"

    else:
        trend = "Lateral"


    # =====================================================
    # PRICE ACTION
    # =====================================================

    candle_range = max(
        float(last["high"] - last["low"]),
        1e-9
    )

    lower_wick = (
        min(last["open"], last["close"])
        - last["low"]
    )

    upper_wick = (
        last["high"]
        - max(last["open"], last["close"])
    )


    # -----------------------------------------------------
    # ENGOLFO DE ALTA
    # -----------------------------------------------------

    engolfo_alta = (
        last["close"] > last["open"]
        and prev["close"] < prev["open"]
        and last["close"] >= prev["open"]
        and last["open"] <= prev["close"]
    )


    # -----------------------------------------------------
    # ENGOLFO DE BAIXA
    # -----------------------------------------------------

    engolfo_baixa = (
        last["close"] < last["open"]
        and prev["close"] > prev["open"]
        and last["open"] >= prev["close"]
        and last["close"] <= prev["open"]
    )


    # -----------------------------------------------------
    # REJEIÇÕES
    # -----------------------------------------------------

    bullish_rejection = (
        lower_wick / candle_range > 0.45
        and last["close"] > last["open"]
    )

    bearish_rejection = (
        upper_wick / candle_range > 0.45
        and last["close"] < last["open"]
    )


    # =====================================================
    # FIBONACCI
    # =====================================================

    swing_high = float(
        df["high"].tail(30).max()
    )

    swing_low = float(
        df["low"].tail(30).min()
    )

    span = max(
        swing_high - swing_low,
        1e-9
    )

    fibs = {
        "38.2%": swing_high - span * 0.382,
        "50.0%": swing_high - span * 0.500,
        "61.8%": swing_high - span * 0.618
    }

    price = float(last["close"])


    # =====================================================
    # DISTÂNCIA DO PREÇO ATÉ FIBONACCI
    # =====================================================

    fib_distance = min(
        abs(price - level) / span
        for level in fibs.values()
    )

    near_fib = fib_distance < 0.12


    # =====================================================
    # PADRÕES
    # =====================================================

    padrao_alta = (
        engolfo_alta
        or bullish_rejection
    )

    padrao_baixa = (
        engolfo_baixa
        or bearish_rejection
    )


    # =====================================================
    # RESULTADO PADRÃO
    # =====================================================

    signal = "AGUARDAR"
    confidence = "Baixa"

    reason = (
        "Os critérios da estratégia "
        "ainda não coincidem."
    )


    # =====================================================
    # COMPRA
    # =====================================================

    if (
        trend == "Alta"
        and padrao_alta
        and near_fib
    ):

        signal = "COMPRA (simulada)"
        confidence = "Alta"

        if engolfo_alta:
            padrao = "engolfo de alta"

        else:
            padrao = "rejeição compradora"

        reason = (
            f"Tendência de alta + {padrao} "
            "+ proximidade de Fibonacci."
        )


    # =====================================================
    # VENDA
    # =====================================================

    elif (
        trend == "Baixa"
        and padrao_baixa
        and near_fib
    ):

        signal = "VENDA (simulada)"
        confidence = "Alta"

        if engolfo_baixa:
            padrao = "engolfo de baixa"

        else:
            padrao = "rejeição vendedora"

        reason = (
            f"Tendência de baixa + {padrao} "
            "+ proximidade de Fibonacci."
        )


    # =====================================================
    # AGUARDAR
    # =====================================================

    else:

        detalhes = []

        detalhes.append(
            f"tendência: {trend.lower()}"
        )

        if padrao_alta or padrao_baixa:
            detalhes.append(
                "padrão de candle identificado"
            )

        else:
            detalhes.append(
                "sem padrão claro"
            )

        if near_fib:
            detalhes.append(
                "próximo de Fibonacci"
            )

        else:
            detalhes.append(
                "longe das zonas de Fibonacci"
            )

        reason = (
            "AGUARDAR: "
            + "; ".join(detalhes)
            + "."
        )


    # =====================================================
    # RETORNO
    # =====================================================

    return {
        "signal": signal,
        "trend": trend,
        "last_price": price,
        "confidence": confidence,
        "reason": reason,
        "fibonacci": fibs
    }
