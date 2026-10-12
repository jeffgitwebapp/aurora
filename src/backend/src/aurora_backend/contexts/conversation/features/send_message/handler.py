"""Caso de uso EnviarMensagem: valida a entrada e devolve a resposta fixa.

O conteúdo da mensagem não é registrado, persistido nem utilizado para compor a resposta.
"""

FIXED_REPLY = "Este chatbot está em desenvolvimento."


class EmptyMessageError(ValueError):
    """Mensagem vazia ou composta apenas por espaços."""


def handle_send_message(message: str) -> str:
    if not message.strip():
        raise EmptyMessageError("A mensagem não pode estar vazia.")
    return FIXED_REPLY
