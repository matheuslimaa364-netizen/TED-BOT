# TED BOT TRADER — versão 2 (protótipo educativo)

## O que esta versão faz
- Painel web em Streamlit.
- Controles de valor simulado, meta, limite de perda, quantidade de sinais e período.
- Botões para iniciar e pausar a simulação.
- Gera candles sintéticos e executa uma análise educativa de tendência, padrões simples de candles e retrações de Fibonacci.
- Mostra o último sinal e mantém um histórico de sinais na sessão atual.

## Instalação local
```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Publicar no Streamlit Community Cloud
No repositório GitHub, envie `app.py`, `strategy.py`, `requirements.txt` e `README.md`.
No Streamlit Community Cloud, selecione o repositório, a branch usada e `app.py` como arquivo principal.

## Limitações importantes
- Usa preços sintéticos (fictícios), não cotações ao vivo.
- Não conecta à Polarium nem a qualquer corretora.
- Não executa operações reais.
- Os sinais são apenas demonstrativos e não foram validados por backtest rigoroso.
- O histórico é mantido na sessão do Streamlit e pode ser perdido quando a sessão reinicia.
- Não é aconselhamento financeiro.
