# =================================================
# TED BOT TRADER - MODULO POLARIUM
# =================================================

class PolariumConnector:
    def __init__(self, modo="DEMO"):
        self.modo = modo
        self.conectado = False

    def conectar(self):
        """
        Prepara a conexao do TED BOT com a Polarium.
        A integracao externa sera adicionada nas proximas etapas.
        """
        self.conectado = True

        return {
            "conectado": True,
            "modo": self.modo,
            "mensagem": f"TED BOT preparado para Polarium - {self.modo}"
        }

    def status(self):
        return {
            "conectado": self.conectado,
            "modo": self.modo
        }
