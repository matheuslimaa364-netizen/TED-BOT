import json
import urllib.request
import urllib.error
import websocket


class DerivConnector:
    def __init__(self, token, app_id):
        self.token = token
        self.app_id = app_id
        self.base_url = "https://api.derivws.com"
        self.ws = None

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Deriv-App-ID": str(self.app_id),
            "Content-Type": "application/json",
        }

    def _request(self, url, method="GET"):
        request = urllib.request.Request(
            url,
            headers=self._headers(),
            method=method
        )

        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                return json.loads(response.read().decode("utf-8"))

        except urllib.error.HTTPError as erro:
            corpo = erro.read().decode("utf-8")

            try:
                dados = json.loads(corpo)
                erros = dados.get("errors", [])

                if erros:
                    mensagem = erros[0].get("message", corpo)
                else:
                    mensagem = corpo
            except Exception:
                mensagem = corpo

            raise Exception(f"HTTP {erro.code}: {mensagem}")

    def conectar(self):
        try:
            # 1. Buscar as contas Options
            contas = self._request(
                f"{self.base_url}/trading/v1/options/accounts"
            )

            dados = contas.get("data", [])

            if isinstance(dados, dict):
                dados = [dados]

            # 2. Procurar somente conta DEMO
            conta_demo = None

            for conta in dados:
                if conta.get("account_type") == "demo":
                    conta_demo = conta
                    break

            if not conta_demo:
                return {
                    "conectado": False,
                    "erro": "Nenhuma conta Options DEMO encontrada."
                }

            account_id = conta_demo.get("account_id")

            # 3. Solicitar OTP para a conta DEMO
            otp = self._request(
                f"{self.base_url}/trading/v1/options/accounts/{account_id}/otp",
                method="POST"
            )

            ws_url = otp.get("data", {}).get("url")

            if not ws_url:
                return {
                    "conectado": False,
                    "erro": "A Deriv não retornou a URL WebSocket."
                }
            ws_segura = ws_url.split("?")[0]

                return {
                    "conectado": False,
                    "erro": f"TESTE URL: {ws_segura}"
                }
            # 4. Conectar imediatamente usando a URL com OTP
            self.ws = websocket.create_connection(
                ws_url,
                timeout=10
            )

            return {
                "conectado": True,
                "is_virtual": True,
                "currency": conta_demo.get("currency", "USD")
            }

        except Exception as erro:
            return {
                "conectado": False,
                "erro": str(erro)
            }

        finally:
            if self.ws:
                try:
                    self.ws.close()
                except Exception:
                    pass
