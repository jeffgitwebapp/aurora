"""Guardrail de saída determinístico (plano §5.5): roda antes de a resposta chegar à usuária.

Regras puras sobre os segmentos gerados. Qualquer violação reprova a resposta inteira;
quem chama trata a reprovação como falha fechada (503).
"""

import re
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass

GUARDRAIL_VERSION = "answer_guardrail@1"
ALLOWED_PHONES = frozenset({"180", "190", "192", "188"})

_FORBIDDEN_PATTERNS: dict[str, tuple[str, ...]] = {
    "diagnosis": (
        r"\bvoce (tem|sofre de|esta com|e|parece ter) (uma |um )?(depressao|ansiedade|"
        r"transtorno|tept|estresse pos|bipolar|borderline|dependencia emocional|trauma)",
        r"\b(seu|o seu) diagnostico\b",
        r"\b(ele|seu marido|seu ex|seu companheiro) (e|tem) (um )?(psicopata|narcisista|"
        r"transtorno)",
    ),
    "prescription": (
        r"\b(tome|tomar|use|usar|recomendo|indico) (o |a |um |uma )?(remedio|medicamento|"
        r"calmante|antidepressivo|ansiolitico|fluoxetina|rivotril|clonazepam|sertralina)",
        r"\b\d+\s?mg\b",
    ),
    "coercive_decision": (
        r"\bvoce (deve|deveria|precisa|tem que) (denunciar|sair|se separar|terminar|"
        r"ligar|ir a delegacia|fazer (um |o )?boletim|perdoar|pedir divorcio)",
        r"\b(denuncie|saia de casa|separe-se|termine com ele|peca o divorcio)\b",
    ),
    "individual_legal_opinion": (
        r"\bno seu caso\b[^.]*\b(e crime|configura|ele sera|ele vai ser|voce vai ganhar|"
        r"voce vai perder)",
        r"\b(ele|seu marido|seu ex|o agressor) (sera|vai ser) (preso|condenado)",
        r"\bo que ele fez (com voce )?(e|foi) crime\b",
    ),
    "acts_on_behalf": (
        r"\b(encaminhei|acionei|liguei|registrei|denunciei|entrei em contato|"
        r"vou ligar|vou denunciar|vou acionar)\b",
    ),
}
_COMPILED = {
    category: tuple(re.compile(pattern) for pattern in patterns)
    for category, patterns in _FORBIDDEN_PATTERNS.items()
}
_URL = re.compile(r"(https?://[^\s)\]>\"”]+|www\.[^\s)\]>\"”]+)", re.IGNORECASE)
# Telefone completo (com ou sem DDD): "(81) 3333-4444", "61 99999-0000", "3333-4444".
_FULL_PHONE = re.compile(r"(?<![\d/.])(?:\(?\d{2}\)?[\s-]?)?\d{4,5}[\s-]\d{4}(?![\d/])")
# Número curto citado como contato: "ligue 181", "disque 100", "WhatsApp: 3333".
_CONTACT_NUMBER = re.compile(
    r"\b(?:ligue|ligar|liga|disque|discar|telefone|tel|whatsapp|zap|numero|contato)\b\D{0,15}?"
    r"(\d{3,})",
    re.IGNORECASE,
)
_DIGIT = re.compile(r"\d")


@dataclass(frozen=True)
class AnswerSegment:
    text: str
    source_ids: tuple[str, ...]


@dataclass(frozen=True)
class AnswerCheck:
    passed: bool
    violations: tuple[str, ...] = ()
    version: str = GUARDRAIL_VERSION


def _normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn").casefold()


def _phones(text: str) -> list[str]:
    without_urls = _URL.sub(" ", text)
    phones = [re.sub(r"\D", "", match.group(0)) for match in _FULL_PHONE.finditer(without_urls)]
    phones.extend(match.group(1) for match in _CONTACT_NUMBER.finditer(_normalize(without_urls)))
    return phones


class AnswerGuardrailService:
    """Reprova respostas sem fonte, fora do escopo ou com contatos/links não autorizados."""

    def check(
        self,
        segments: Iterable[AnswerSegment],
        *,
        allowed_source_ids: frozenset[str],
        allowed_urls: frozenset[str],
    ) -> AnswerCheck:
        segments = tuple(segments)
        violations: list[str] = []
        if not segments or not any(segment.text.strip() for segment in segments):
            violations.append("empty_answer")
        if not any(segment.source_ids for segment in segments):
            violations.append("no_citation")
        if any(
            source_id not in allowed_source_ids
            for segment in segments
            for source_id in segment.source_ids
        ):
            violations.append("unknown_source_id")

        for segment in segments:
            normalized = _normalize(segment.text)
            for category, patterns in _COMPILED.items():
                if any(pattern.search(normalized) for pattern in patterns):
                    violations.append(category)
            phones = _phones(segment.text)
            if any(phone not in ALLOWED_PHONES for phone in phones):
                violations.append("unauthorized_contact")
            for url in _URL.findall(segment.text):
                if url.rstrip(".,;:") not in allowed_urls:
                    violations.append("unauthorized_link")
            without_allowed_phones = segment.text
            for phone in ALLOWED_PHONES:
                without_allowed_phones = without_allowed_phones.replace(phone, "")
            if not segment.source_ids and _DIGIT.search(without_allowed_phones):
                violations.append("uncited_fact")

        unique = tuple(dict.fromkeys(violations))
        return AnswerCheck(passed=not unique, violations=unique)
