"""Reconhece relato pessoal de violência para acolher quando não há fonte (U-14).

Determinístico e sem LLM, no mesmo texto normalizado da triagem. Só é consultado
depois que a busca não encontra fonte: troca o "não sei" genérico por um texto de
acolhimento, sem afirmar fatos. Risco agudo continua com a triagem, que roda antes.
Lista provisória, pendente da revisão da psicóloga.
"""

import re

from aurora_backend.contexts.conversation.services.triage.service import normalize_for_triage

_AGGRESSOR = (
    r"\b(ele|marido|esposo|namorado|noivo|companheiro|parceiro|ex|pai|padrasto|"
    r"irmao|filho|sogro|sogra|chefe)\b"
)
_ABUSE = (
    r"\b(grit\w*|berr\w*|xing\w*|humilh\w*|ofend\w*|ameac\w*|control\w*|proib\w*|"
    r"persegu\w*|vigi\w*|espion\w*|chantage\w*|manipul\w*|desvaloriz\w*|ridiculariz\w*|"
    r"isol\w*|agred\w*|agress\w*|empurr\w*|machuc\w*|bat(e|eu|endo|ia|er)|"
    r"me (chama|chamou|chamava) de|nao me deixa\w*|me obrig\w*|me forc\w*)\b"
)
_FEELING = re.compile(
    r"\b(estou|to|tou|ando|fico|vivo|sinto|tenho)( \w+)? (com )?"
    r"(medo|pavor|apavorad\w*|assustad\w*)\b"
    r"|\bnao aguento mais\b"
    r"|\bme sinto (humilhad\w*|sozinh\w*|pres\w*|culpad\w*|um lixo|inutil|sufocad\w*)\b"
    r"|\b(sofro|sofrendo|sofri|vivo|vivendo) (violencia|abuso|agress\w*)\b"
)
_AGGRESSOR_RE = re.compile(_AGGRESSOR)
_ABUSE_RE = re.compile(_ABUSE)


class DisclosureService:
    async def is_disclosure(self, message: str) -> bool:
        text = normalize_for_triage(message)
        if not text:
            return False
        if _FEELING.search(text):
            return True
        return bool(_AGGRESSOR_RE.search(text) and _ABUSE_RE.search(text))
