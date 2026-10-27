import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from strategy import generate_demo_candles, analyze_market

st.set_page_config(page_title="TED BOT TRADER", page_icon="📈", layout="wide")

if "history" not in st.session_state:
    st.session_state.history = []
if "running" not in st.session_state:
    st.session_state.running = False
if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = None

st.title("📈 TED BOT TRADER")
st.caption("Protótipo de estudo — Price Action + Fibonacci | Somente simulação")

with st.sidebar:
    st.header("⚙️ Configurações")
    entry_amount = st.number_input("Valor de entrada (simulado)", min_value=1.0, max_value=10000.0, value=10.0, step=1.0)
    daily_target = st.number_input("Meta diária simulada", min_value=1.0, max_value=100000.0, value=50.0, step=5.0)
    daily_loss_limit = st.number_input("Limite de perda simulado", min_value=1.0, max_value=100000.0, value=30.0, step=5.0)
    max_signals = st.number_input("Máximo de sinais por sessão", min_value=1, max_value=500, value=10, step=1)
    timeframe = st.selectbox("Período gráfico", ["M1", "M5", "M15"], index=1)
    martingale = st.checkbox("Martingale (desativado por segurança)", value=False, disabled=True)
    st.caption("Os valores são parâmetros demonstrativos; não controlam operações reais.")

    st.divider()
    st.subheader("Modo")
    st.info("SIMULAÇÃO — não conectado à corretora")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Estado", "Executando simulação" if st.session_state.running else "Pausado")
with col2:
    st.metric("Sinais nesta sessão", len(st.session_state.history), f"Limite: {int(max_signals)}")
with col3:
    st.metric("Período", timeframe)

left, right = st.columns([1, 1])
with left:
    if st.button("▶️ Iniciar simulação", type="primary", use_container_width=True):
        st.session_state.running = True
        candles = generate_demo_candles(timeframe=timeframe, seed=int(datetime.now().timestamp()) % 100000)
        result = analyze_market(candles)
        st.session_state.last_analysis = result
        if result["signal"] != "AGUARDAR" and len(st.session_state.history) < int(max_signals):
            st.session_state.history.insert(0, {
                "Horário": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "Período": timeframe,
                "Sinal": result["signal"],
                "Preço simulado": round(result["last_price"], 5),
                "Tendência": result["trend"],
                "Motivo": result["reason"],
                "Resultado": "PENDENTE (simulação)"
            })
        st.rerun()
with right:
    if st.button("⏸️ Pausar simulação", use_container_width=True):
        st.session_state.running = False
        st.rerun()

if st.session_state.running:
    st.success("Simulação ativa. Clique em “Iniciar simulação” novamente para gerar uma nova análise demonstrativa.")
else:
    st.warning("Simulação pausada. Nenhuma operação real está sendo executada.")

st.subheader("🔎 Última análise demonstrativa")
if st.session_state.last_analysis is None:
    st.info("Clique em “Iniciar simulação” para gerar uma análise com candles fictícios.")
else:
    result = st.session_state.last_analysis
    a, b, c, d = st.columns(4)
    a.metric("Sinal", result["signal"])
    b.metric("Tendência", result["trend"])
    c.metric("Preço fictício", f'{result["last_price"]:.5f}')
    d.metric("Força do sinal", result["confidence"])
    st.write("**Justificativa:**", result["reason"])
    st.write("**Níveis de Fibonacci calculados (referência):**")
    fibs = result["fibonacci"]
    f1, f2, f3 = st.columns(3)
    f1.metric("38,2%", f'{fibs["38.2%"]:.5f}')
    f2.metric("50%", f'{fibs["50.0%"]:.5f}')
    f3.metric("61,8%", f'{fibs["61.8%"]:.5f}')

st.subheader("📊 Candles fictícios usados na análise")
candles = generate_demo_candles(timeframe=timeframe, seed=42)
st.line_chart(candles.set_index("time")[["close"]], height=220)
st.caption("Gráfico criado com preços sintéticos para testar a interface e a lógica. Não representa cotações atuais.")

st.subheader("🧾 Histórico de sinais da sessão")
if st.session_state.history:
    st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True, hide_index=True)
    if st.button("🗑️ Limpar histórico da sessão"):
        st.session_state.history = []
        st.rerun()
else:
    st.write("Nenhum sinal registrado ainda. A estratégia pode retornar AGUARDAR quando os critérios não forem atendidos.")

st.divider()
st.caption("Aviso: projeto educacional em simulação. Não é recomendação financeira, não está conectado à corretora e não executa compras ou vendas reais.")
