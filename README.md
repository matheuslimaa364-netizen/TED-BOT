# TED BOT TRADER — protótipo demonstrativo

Painel inicial em Streamlit para estudar Price Action + Fibonacci e gerenciamento de risco.

## O que está incluído
- Painel web com valor por entrada, meta diária, limite de perda e máximo de sinais.
- Seleção de tempo gráfico M1/M5/M15.
- Visualização de dados fictícios.
- Heurística didática de direção, rejeição de candle e região de Fibonacci.
- Histórico local de sinais durante a sessão.
- Botões para iniciar/parar a análise local.

## O que NÃO está incluído
- Não conecta à Polarium.
- Não acessa cotações reais.
- Não envia ordens nem executa operações.
- Não garante lucro nem valida uma estratégia lucrativa.
- O saldo e os resultados não são resultados reais.

## Rodar no computador
Requer Python 3.10 ou superior.

```bash
python -m venv .venv
```

Windows:
```bash
.venv\\Scripts\\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Instale dependências e rode:
```bash
pip install -r requirements.txt
streamlit run app.py
```

O Streamlit exibirá um endereço local para abrir no navegador.

## Publicar na nuvem
Pode ser publicado em um serviço que aceite aplicações Python/Streamlit. Envie estes arquivos para um repositório Git e configure o comando de inicialização:

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port $PORT
```

Em alguns serviços, a variável de porta tem outro nome. Siga a documentação do provedor escolhido.

## Próximos passos antes de qualquer integração real
1. Obter confirmação por escrito da Polarium sobre API oficial e permissões de automação.
2. Definir fonte autorizada de cotações e validar diferenças de preço.
3. Fazer backtest com dados reais adequados e custos.
4. Criar testes unitários, logs persistentes e proteção contra ordens duplicadas.
5. Implementar autenticação segura e armazenamento de segredos fora do código.
6. Começar em demo. Não inserir senhas, cookies ou tokens no painel.
