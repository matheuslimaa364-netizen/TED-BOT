import json
import websocket


class DerivConnector:
    def __init__(self, token, app_id):
        self.token = token
        self.app_id = app_id
        self.ws = None

    def conectar(self):
        try:
            url = f"wss://ws.derivws.com/websockets/v3?app_id={self.app_id}"

            self.ws = websocket.create_connection(
                url,
                timeout=10
            )

            self.ws.send(
                json.dumps({
                    "authorize": self.token
                })
            )

            resposta = json.loads(self.ws.recv())

            if "error" in resposta:
                return {
                    "conectado": False,
                    "erro": resposta["error"].get(
                        "message",
                        "Erro ao conectar."
                    )
                }

            authorize = resposta.get("authorize", {})

            return {
                "conectado": True,
                "loginid": authorize.get("loginid", ""),
                "currency": authorize.get("currency", ""),
                "is_virtual": authorize.get("is_virtual", False)
            }

        except Exception as erro:
            return {
                "conectado": False,
                "erro": str(erro)
            }

        finally:
            if self.ws:
                self.ws.close()
