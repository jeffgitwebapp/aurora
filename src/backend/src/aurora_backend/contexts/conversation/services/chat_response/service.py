"""Serviço de resposta da conversa com conteúdo estático de protótipo."""

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


class ChatResponseService:
    """Gera texto demonstrativo; a implementação será integrada ao LLM aprovado."""

    async def generate_reply(self, message: str) -> str:
        del message
        paragraph = " ".join(
            (
                random.choice(_SCENES),
                random.choice(_DEVELOPMENTS),
                random.choice(_CLOSINGS),
            )
        )
        return f"{SIMULATED_REPLY_PREFIX}: {paragraph}"
