"""Reconhece mensagens que são só saudação, agradecimento ou despedida (U-11).

Determinístico e sem LLM: o backend decide e devolve o texto da resposta (`reply`);
o front só exibe. Só reconhece a mensagem inteira; se houver conteúdo além da saudação
("oi, meu marido me ameaça"), a mensagem segue o fluxo normal. Roda depois da
triagem e do limite de escopo.
"""

import re
import unicodedata
from dataclasses import dataclass
from enum import StrEnum


class ConversationKind(StrEnum):
    GREETING = "greeting"
    THANKS = "thanks"
    FAREWELL = "farewell"


_GREETING = r"(oi+e?|ola|opa|hey|e ai|eai|alo|bom dia|boa tarde|boa noite|tudo bem|tudo bom|td bem)"
_POLITE = r"(aurora|tudo bem|tudo bom|td bem|como vai|como voce esta|alguem ai|tem alguem ai)"
_PATTERNS: tuple[tuple[ConversationKind, re.Pattern[str]], ...] = (
    (
        ConversationKind.GREETING,
        re.compile(rf"^({_GREETING}|{_POLITE})( {_GREETING}| {_POLITE})*$"),
    ),
    (
        ConversationKind.THANKS,
        re.compile(
            r"^(muito )?(obrigad[oa]s?|obg|brigad[oa]|valeu|agradeco)"
            r"( (muito|mesmo|demais|pela ajuda|aurora))*$"
        ),
    ),
    (
        ConversationKind.FAREWELL,
        re.compile(r"^(tchau|ate mais|ate logo|ate depois|adeus|fui|xau)( (aurora|obrigad[oa]))*$"),
    ),
)


def _normalize(message: str) -> str:
    decomposed = unicodedata.normalize("NFKD", message)
    without_accents = "".join(c for c in decomposed if unicodedata.category(c) != "Mn")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", without_accents.casefold()).split())


# Textos definidos pelo backend; o front só exibe. Revisão da psicóloga pendente.
REPLIES: dict[ConversationKind, str] = {
    ConversationKind.GREETING: (
        "Olá. Estou aqui para ajudar com informações sobre violência psicológica, direitos "
        "e onde buscar apoio.\n\n"
        "Você pode contar com suas palavras o que está acontecendo ou fazer uma pergunta, "
        "por exemplo: O que é violência psicológica?\n\n"
        "Se estiver em perigo agora, os contatos de emergência estão nesta tela."
    ),
    ConversationKind.THANKS: (
        "De nada. Se quiser, pode continuar perguntando ou contar o que está acontecendo. "
        "Você decide o que compartilhar."
    ),
    ConversationKind.FAREWELL: (
        "Até logo. Cuide-se. Esta conversa é descartada quando você fecha a página. "
        "Se precisar sair rápido, use o botão Saída rápida ou a tecla Esc."
    ),
}


@dataclass(frozen=True)
class SmallTalkReply:
    kind: ConversationKind
    text: str


class SmallTalkService:
    async def respond(self, message: str) -> SmallTalkReply | None:
        text = _normalize(message)
        if not text:
            return None
        kind = next((kind for kind, pattern in _PATTERNS if pattern.match(text)), None)
        return SmallTalkReply(kind=kind, text=REPLIES[kind]) if kind is not None else None
