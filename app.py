import streamlit as st
import pandas as pd
from datetime import datetime

from strategy import generate_demo_candles, analyze_market


# =========================================================
# CONFIGURACAO DA PAGINA
# =========================================================

st.set_page_config(
    page_title="TED BOT TRADER",
    page_icon="📈",
    layout="wide"
)

st.title("📈 TED BOT TRADER")
st.caption(
    "Protótipo de estudo — Price Action + Fibonacci | "
    "Somente simulação"
)


# =========================================================
# ESTADO DA SESSAO
# =========================================================

if "running" not in st.session_state:
    st.session_state.running = False

if "history" not in st.session_state:
    st.session_state.history = []

if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = None

if "lucro_sessao" not in st.session_state:
    st.session_state.lucro_sessao = 0.0

if "last_candles" not in st.session_state:
    st.session_state.last_candles = None


# =========================================================
# CONFIGURACOES
# =========================================================

st.sidebar.header("⚙️ Configurações")

entry_amount = st.sidebar.number_input(
    "Valor de entrada (simulado)",
    min_value=1.0,
    value=10.0,
    step=1.0
)

daily_target = st.sidebar.number_input(
    "Meta diária simulada",
    min_value=1.0,
    value=50.0,
    step=5.0
)

daily_loss_limit = st.sidebar.number_input(
    "Limite de perda simulado",
    min_value=1.0,
    value=30.0,
    step=5.0
)

max_signals = st.sidebar.number_input(
    "Máximo de sinais por sessão",
    min_value=1,
    value=10,
    step=1
)

timeframe = st.sidebar.selectbox(
    "Período gráfico",
    ["M1", "M5", "M15"]
)

st.sidebar.checkbox(
    "Martingale (desativado por segurança)",
    value=False,
    disabled=True
)

st.sidebar.caption(
    "Os valores são parâmetros demonstrativos; "
    "não controlam operações reais."
)


# =========================================================
# PAINEL PRINCIPAL
# =========================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    estado = (
        "Executando simulação"
        if st.session_state.running
        else "Pausado"
    )

    st.metric(
        "Estado",
        estado
    )

with col2:
    st.metric(
        "Sinais nesta sessão",
        len(st.session_state.history)
    )

    st.caption(
        f"Limite: {int(max_signals)}"
    )

with col3:
    st.metric(
        "Período",
        timeframe
    )

with col4:
    st.metric(
        "Lucro da sessão",
        f"R$ {st.session_state.lucro_sessao:.2f}"
    )


# =========================================================
# BOTOES
# =========================================================

left, right = st.columns([1, 1])


# =========================================================
# INICIAR SIMULACAO
# =========================================================

with left:

    if st.button(
        "▶️ Iniciar simulação",
        type="primary",
        use_container_width=True
    ):

        st.session_state.running = True

        # -------------------------------------------------
        # GERA UMA UNICA SEQUENCIA DE CANDLES
        # -------------------------------------------------

        seed = int(
            datetime.now().timestamp()
        ) % 100000

        candles = generate_demo_candles(
            timeframe=timeframe,
            periods=105,
            seed=seed
        )

        st.session_state.last_candles = candles


        # -------------------------------------------------
        # SEPARA PASSADO E FUTURO
        #
        # Os primeiros 100 candles sao usados na analise.
        # Os 5 ultimos representam candles posteriores.
        # -------------------------------------------------

        analysis_candles = candles.iloc[:100].copy()

        future_candles = candles.iloc[100:].copy()


        # -------------------------------------------------
        # ANALISA SOMENTE OS CANDLES ANTERIORES
        # -------------------------------------------------

        result = analyze_market(
            analysis_candles
        )

        st.session_state.last_analysis = result


        # -------------------------------------------------
        # REGISTRA SOMENTE COMPRA OU VENDA
        # -------------------------------------------------

        if (
            result["signal"] != "AGUARDAR"
            and
            len(st.session_state.history)
            < int(max_signals)
        ):

            # Preco no momento do sinal
            preco_entrada = float(
                analysis_candles.iloc[-1]["close"]
            )

            # Preco apos os candles seguintes
            preco_saida = float(
                future_candles.iloc[-1]["close"]
            )


            # ---------------------------------------------
            # RESULTADO DA OPERACAO
            # ---------------------------------------------

            if "COMPRA" in result["signal"]:

                if preco_saida > preco_entrada:
                    resultado_operacao = "WIN ✅"

                else:
                    resultado_operacao = "LOSS ❌"

            else:

                if preco_saida < preco_entrada:
                    resultado_operacao = "WIN ✅"

                else:
                    resultado_operacao = "LOSS ❌"


            # ---------------------------------------------
            # ATUALIZA LUCRO
            # ---------------------------------------------

            if resultado_operacao == "WIN ✅":

                st.session_state.lucro_sessao += (
                    entry_amount * 0.85
                )

            else:

                st.session_state.lucro_sessao -= (
                    entry_amount
                )


            # ---------------------------------------------
            # VERIFICA META
            # ---------------------------------------------

            if (
                st.session_state.lucro_sessao
                >= daily_target
            ):

                st.session_state.running = False


            # ---------------------------------------------
            # VERIFICA LIMITE DE PERDA
            # ---------------------------------------------

            if (
                st.session_state.lucro_sessao
                <= -daily_loss_limit
            ):

                st.session_state.running = False


            # ---------------------------------------------
            # SALVA NO HISTORICO
            # ---------------------------------------------

            st.session_state.history.insert(
                0,
                {
                    "Horário":
                        datetime.now().strftime(
                            "%d/%m/%Y %H:%M:%S"
                        ),

                    "Período":
                        timeframe,

                    "Sinal":
                        result["signal"],

                    "Preço entrada":
                        round(
                            preco_entrada,
                            5
                        ),

                    "Preço saída":
                        round(
                            preco_saida,
                            5
                        ),

                    "Tendência":
                        result["trend"],

                    "Confiança":
                        result["confidence"],

                    "Motivo":
                        result["reason"],

                    "Resultado":
                        resultado_operacao
                }
            )

        st.rerun()


# =========================================================
# PAUSAR
# =========================================================

with right:

    if st.button(
        "⏸️ Pausar simulação",
        use_container_width=True
    ):

        st.session_state.running = False

        st.rerun()


# =========================================================
# STATUS
# =========================================================

if (
    st.session_state.lucro_sessao
    >= daily_target
):

    st.success(
        "🎯 Meta diária atingida! "
        "Simulação pausada automaticamente."
    )

elif (
    st.session_state.lucro_sessao
    <= -daily_loss_limit
):

    st.error(
        "🔴 Limite de perda atingido! "
        "Simulação pausada automaticamente."
    )

elif st.session_state.running:

    st.success(
        'Simulação ativa. Clique em "Iniciar simulação" '
        "novamente para gerar uma nova análise demonstrativa."
    )

else:

    st.warning(
        "Simulação pausada. "
        "Nenhuma operação real está sendo executada."
    )


# =========================================================
# ULTIMA ANALISE
# =========================================================

st.subheader(
    "🔎 Última análise demonstrativa"
)

if st.session_state.last_analysis is None:

    st.info(
        'Clique em "Iniciar simulação" para gerar '
        "uma análise com candles fictícios."
    )

else:

    result = st.session_state.last_analysis

    a, b, c, d = st.columns(4)

    with a:

        st.metric(
            "Sinal",
            result["signal"]
        )

    with b:

        st.metric(
            "Tendência",
            result["trend"]
        )

    with c:

        st.metric(
            "Preço fictício",
            f'{result["last_price"]:.5f}'
        )

    with d:

        st.metric(
            "Força do sinal",
            result["confidence"]
        )

    st.write(
        "**Justificativa:**",
        result["reason"]
    )


    # =====================================================
    # FIBONACCI
    # =====================================================

    st.write(
        "**Níveis de Fibonacci calculados (referência):**"
    )

    fibonacci = result.get(
        "fibonacci",
        {}
    )

    if fibonacci:

        fib_cols = st.columns(
            len(fibonacci)
        )

        for coluna, (nivel, valor) in zip(
            fib_cols,
            fibonacci.items()
        ):

            with coluna:

                st.metric(
                    nivel,
                    f"{float(valor):.5f}"
                )


# =========================================================
# GRAFICO DA ULTIMA SEQUENCIA
# =========================================================

st.subheader(
    "📊 Gráfico demonstrativo"
)

if st.session_state.last_candles is not None:

    dados_grafico = (
        st.session_state.last_candles[
            ["close"]
        ].copy()
    )

    dados_grafico.columns = [
        "Preço sintético"
    ]

    st.line_chart(
        dados_grafico
    )

else:

    grafico = generate_demo_candles(
        timeframe=timeframe,
        periods=105,
        seed=12345
    )

    dados_grafico = grafico[
        ["close"]
    ].copy()

    dados_grafico.columns = [
        "Preço sintético"
    ]

    st.line_chart(
        dados_grafico
    )

st.caption(
    "Gráfico criado com preços sintéticos para testar "
    "a interface e a lógica. Não representa cotações atuais."
)


# =========================================================
# HISTORICO
# =========================================================

st.subheader(
    "📋 Histórico de sinais da sessão"
)

if len(st.session_state.history) > 0:

    historico_df = pd.DataFrame(
        st.session_state.history
    )

    st.dataframe(
        historico_df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "Nenhum sinal registrado nesta sessão."
    )


# =========================================================
# LIMPAR HISTORICO
# =========================================================

if st.button(
    "🗑️ Limpar histórico da sessão"
):

    st.session_state.history = []

    st.session_state.lucro_sessao = 0.0

    st.session_state.last_analysis = None

    st.session_state.last_candles = None

    st.rerun()


# =========================================================
# NOVA SESSAO
# =========================================================

if st.button(
    "🔄 Nova sessão"
):

    st.session_state.history = []

    st.session_state.lucro_sessao = 0.0

    st.session_state.last_analysis = None

    st.session_state.last_candles = None

    st.session_state.running = False

    st.rerun()


# =========================================================
# AVISO
# =========================================================

st.divider()

st.caption(
    "TED BOT TRADER — Ambiente educacional e demonstrativo. "
    "Os candles, preços, sinais e resultados apresentados "
    "são simulados."
)
