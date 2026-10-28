"""Caso de uso EnviarMensagem: valida a entrada e gera texto simulado.

O conteúdo da mensagem não é registrado, persistido nem utilizado para compor a resposta.
"""

import random

SIMULATED_REPLY_PREFIX = "ATENÇÃO ISSO NÃO É ACONSELHAMENTO, APENAS TEXTO SIMULADO"

_SCENES = (
    "No panorama das possibilidades, diferentes elementos se encontram em constante transformação.",
    "Em uma dinâmica ampla, ideias e contextos se conectam de maneiras variadas.",
    "A composição desse cenário reúne perspectivas que seguem em movimento.",
)

_DEVELOPMENTS = (
    "Cada etapa acrescenta uma nova camada a esse cenário.",
    "Os caminhos se reorganizam conforme novas perspectivas entram em cena.",
    "Os elementos dessa dinâmica se articulam em diferentes direções.",
)

_CLOSINGS = (
    "O resultado permanece aberto, sem apontar para uma conclusão prática.",
    "Essa composição segue em movimento, sem indicar uma orientação concreta.",
    "Assim, o cenário continua em construção, sem oferecer recomendações.",
)


class EmptyMessageError(ValueError):
    """Mensagem vazia ou composta apenas por espaços."""


def _generate_simulated_reply() -> str:
    paragraph = " ".join(
        (
            random.choice(_SCENES),
            random.choice(_DEVELOPMENTS),
            random.choice(_CLOSINGS),
        )
    )
    return f"{SIMULATED_REPLY_PREFIX}: {paragraph}"


def handle_send_message(message: str) -> str:
    if not message.strip():
        raise EmptyMessageError("A mensagem não pode estar vazia.")
    return _generate_simulated_reply()
