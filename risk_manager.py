def verificar_risco(
    lucro_sessao,
    meta_diaria,
    limite_perda,
    sinais_realizados,
    max_sinais
):
    """
    Gerenciamento interno de risco do TED BOT TRADER.
    """

    if lucro_sessao >= meta_diaria:
        return {
            "permitido": False,
            "motivo": "Meta diária atingida."
        }

    if lucro_sessao <= -limite_perda:
        return {
            "permitido": False,
            "motivo": "Limite de perda atingido."
        }

    if sinais_realizados >= max_sinais:
        return {
            "permitido": False,
            "motivo": "Limite máximo de sinais atingido."
        }

    return {
        "permitido": True,
        "motivo": "Gerenciamento de risco liberado."
    }
