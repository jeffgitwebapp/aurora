"""Serviço de triagem com regras estáticas para o protótipo atual."""

import re
import unicodedata

from aurora_backend.contexts.conversation.services.triage.models import (
    TriageResult,
    TriageSignal,
    TriageStatus,
)

_RISK_FIXTURES: dict[TriageSignal, tuple[str, ...]] = {
    TriageSignal.SUICIDAL_IDEATION: (
        "Estou pensando em me matar",
        "Quero tirar minha vida",
    ),
    TriageSignal.ONGOING_ASSAULT: (
        "Ele está me agredindo agora",
        "Estou sendo atacada neste momento",
    ),
    TriageSignal.DEATH_THREAT: (
        "Ele disse que vai me matar",
        "Recebi uma ameaça de morte",
    ),
    TriageSignal.WEAPON_PRESENT: (
        "Ele está com uma arma aqui",
        "Há uma arma no local agora",
    ),
}

_INDETERMINATE_FIXTURE = "frase incerta"
_SENTENCE_SEPARATOR = re.compile(r"[.!?;\n]+")
_SIGNAL_LABELS = {
    TriageSignal.SUICIDAL_IDEATION: "ideação suicida",
    TriageSignal.ONGOING_ASSAULT: "agressão em curso",
    TriageSignal.DEATH_THREAT: "ameaça de morte",
    TriageSignal.WEAPON_PRESENT: "presença de arma",
}


def _normalize_fixture_sentence(sentence: str) -> str:
    decomposed = unicodedata.normalize("NFKD", sentence)
    without_accents = "".join(
        character for character in decomposed if unicodedata.category(character) != "Mn"
    )
    return " ".join(without_accents.casefold().split()).strip(" \t\r\n.,;:!?")


_NORMALIZED_RISK_FIXTURES = {
    signal: {_normalize_fixture_sentence(phrase) for phrase in phrases}
    for signal, phrases in _RISK_FIXTURES.items()
}
_NORMALIZED_INDETERMINATE_FIXTURE = _normalize_fixture_sentence(_INDETERMINATE_FIXTURE)


class TriageService:
    """Avalia as fixtures estáticas atuais; não avalia risco real."""

    async def assess(self, message: str) -> TriageResult:
        normalized_segments = [
            _normalize_fixture_sentence(segment)
            for segment in _SENTENCE_SEPARATOR.split(message)
            if segment.strip()
        ]
        if not normalized_segments:
            return TriageResult(status=TriageStatus.NO_ACUTE_SIGNAL)

        matched_signals: list[TriageSignal] = []
        for segment in normalized_segments:
            matching_signal = next(
                (
                    signal
                    for signal, fixtures in _NORMALIZED_RISK_FIXTURES.items()
                    if segment in fixtures
                ),
                None,
            )
            if matching_signal is not None and matching_signal not in matched_signals:
                matched_signals.append(matching_signal)

        if matched_signals:
            labels = ", ".join(_SIGNAL_LABELS[signal] for signal in matched_signals)
            return TriageResult(
                status=TriageStatus.ACUTE,
                signals=tuple(matched_signals),
                guidance=(
                    "Simulação do protótipo: fixture de teste reconhecida para "
                    f"{labels}. Nenhuma resposta informativa foi gerada. "
                    "Esta simulação não avalia situações reais. Se precisar de "
                    "apoio, os contatos úteis estão disponíveis nesta tela."
                ),
            )

        if (
            len(normalized_segments) == 1
            and normalized_segments[0] == _NORMALIZED_INDETERMINATE_FIXTURE
        ):
            return self._indeterminate_result()

        return TriageResult(status=TriageStatus.NO_ACUTE_SIGNAL)

    @staticmethod
    def _indeterminate_result() -> TriageResult:
        return TriageResult(
            status=TriageStatus.INDETERMINATE,
            guidance=(
                "Simulação inconclusiva: a mensagem não corresponde às frases de "
                "teste configuradas. Nenhuma resposta informativa foi gerada. "
                "Isso não significa ausência de risco; esta simulação não avalia "
                "situações reais."
            ),
        )
