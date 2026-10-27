import streamlit as st
import pandas as pd
from datetime import datetime
from strategy import generate_demo_candles, analyze_market

st.set_page_config(page_title="TED BOT TRADER", page_icon="📈", layout="wide")

if "running" not in st.session_state:
    st.session_state.running = False
if "history" not in st.session_state:
    st.session_state.history = []
if "candles" not in st.session_state:
    st.session_state.candles = generate_demo_candles()

st.markdown("""
<style>
.stApp { background: #0b1220; color: #e5e7eb; }
[data-testid="stMetric"] { background: #172235; padding: 14px; border-radius: 12px; }
section[data-testid="stSidebar"] { background: #101a2b; }
</style>
""", unsafe_allow_html=True)

st.title("📈 TED BOT TRADER")
st.caption("Price Action + Fibonacci • Painel demonstrativo • Sem conexão com a Polarium")

with st.sidebar:
    st.header("⚙️ Gerenciamento")
    mode = st.selectbox("Modo", ["Simulação (demo)", "Somente sinais"])
    entry = st.number_input("Valor por entrada (R$)", min_value=1.0, value=10.0, step=1.0)
    daily_target = st.number_input("Meta diária (R$)", min_value=1.0, value=50.0, step=5.0)
    daily_stop = st.number_input("Limite de perda diária (R$)", min_value=1.0, value=30.0, step=5.0)
    max_trades = st.number_input("Máximo de sinais por sessão", min_value=1, max_value=100, value=5, step=1)
    timeframe = st.selectbox("Tempo gráfico", ["M1", "M5", "M15"], index=1)
    martingale = st.checkbox("Martingale", value=False, help="Desativado por padrão. Não é recomendado para operações reais.")
    st.divider()
    st.warning("Este protótipo não envia ordens e não está conectado a uma conta.")
    start = st.button("▶ Iniciar análise", use_container_width=True)
    stop = st.button("⏸ Pausar robô", use_container_width=True)
    refresh = st.button("🔄 Gerar novo cenário demo", use_container_width=True)

if start:
    st.session_state.running = True
if stop:
    st.session_state.running = False
if refresh:
    st.session_state.candles = generate_demo_candles()

candles = st.session_state.candles
analysis = analyze_market(candles)
signals_count = len(st.session_state.history)
session_pnl = sum(item["Resultado (R$)"] for item in st.session_state.history)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Saldo demonstrativo", "R$ 1.000,00")
c2.metric("Resultado registrado", f"R$ {session_pnl:.2f}")
c3.metric("Sinais registrados", str(signals_count))
c4.metric("Estado", "Analisando" if st.session_state.running else "Pausado")

st.divider()
left, right = st.columns([1.4, 1])

with left:
    st.subheader("📊 Cenário de mercado (dados fictícios)")
    chart_df = candles.set_index("Hora")[["Fechamento"]]
    st.line_chart(chart_df)
    st.caption("Gráfico ilustrativo criado localmente. Não representa preços reais.")

with right:
    st.subheader("🧭 Leitura Price Action + Fibonacci")
    st.write(f"**Direção estimada:** {analysis['direcao']}")
    st.write(f"**Estrutura:** {analysis['estrutura']}")
    st.write(f"**Padrão:** {analysis['padrao']}")
    st.write(f"**Região Fibonacci:** {analysis['fib_regiao']}")
    st.write(f"**Sinal didático:** {analysis['sinal']}")
    st.write(f"**Motivo:** {analysis['motivo']}")
    st.info("Sinais didáticos não são recomendações financeiras nem previsões confiáveis.")

    if st.session_state.running and analysis["sinal"] != "AGUARDAR":
        if len(st.session_state.history) < max_trades:
            already = st.session_state.history and st.session_state.history[-1]["Sinal"] == analysis["sinal"]
            if not already:
                st.session_state.history.append({
                    "Horário": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Sinal": analysis["sinal"],
                    "Valor configurado (R$)": float(entry),
                    "Resultado (R$)": 0.0,
                    "Modo": mode,
                    "Tempo gráfico": timeframe
                })
                st.rerun()

    if st.session_state.running:
        st.caption("Análise local ativa. Não há execução automática de ordens.")

st.divider()
st.subheader("🛡️ Proteções de gerenciamento")
p1, p2, p3 = st.columns(3)
p1.metric("Meta diária", f"R$ {daily_target:.2f}")
p2.metric("Limite de perda", f"R$ {daily_stop:.2f}")
p3.metric("Limite de sinais", f"{max_trades}")
if session_pnl >= daily_target:
    st.success("Meta registrada atingida. Em uma versão conectada, o sistema deve bloquear novas entradas.")
elif session_pnl <= -daily_stop:
    st.error("Limite de perda atingido. Em uma versão conectada, o sistema deve bloquear novas entradas.")
else:
    st.caption("Os limites estão configurados, mas o P&L deste protótipo não é atualizado com resultados reais.")

st.subheader("🧾 Histórico")
if st.session_state.history:
    st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True, hide_index=True)
else:
    st.write("Nenhum sinal registrado ainda.")
if st.button("Limpar histórico", type="secondary"):
    st.session_state.history = []
    st.rerun()

st.divider()
st.caption("Versão inicial de demonstração. Antes de operar dinheiro real: testar a estratégia, validar dados e confirmar integração oficial autorizada da plataforma.")
