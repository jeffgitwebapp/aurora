"""Triagem determinística de risco agudo por padrões (U-10), antes de qualquer LLM.

Os padrões procuram expressões em qualquer ponto da mensagem, sem acento e sem
diferença de caixa. Na dúvida, preferem o falso positivo ao falso negativo (RNF03).
A lista é PROVISÓRIA: depende da curadoria especializada do CA-02 e não garante a
detecção de todas as formas de pedir ajuda.
"""

import re
import unicodedata

from aurora_backend.contexts.conversation.services.triage.models import (
    TriageResult,
    TriageSignal,
    TriageStatus,
)
from aurora_backend.shared.fixture_text import (
    normalize_fixture_sentence,
)

_FIRST_PERSON_INTENT = (
    r"(quero|queria|vou|iria|penso em|pensando em|pensei em|pensado em|vontade de|"
    r"tentei|tentar|tentando|preciso|planejando|decidi)"
)
_AGGRESSOR = r"(ele|ela|marido|ex|namorado|companheiro|parceiro|pai|padrasto|filho|irmao)"
_ASSAULT_VERB = (
    r"(batendo|agredindo|espancando|machucando|enforcando|estrangulando|"
    r"esfaqueando|atacando|chutando|socando|sufocando|empurrando)"
)
_WEAPON = r"\b(arma|armas|armado|armada|revolver|pistola|espingarda|faca|facas|facao|canivete)\b"
_WEAPON_CONTEXT = (
    r"\b(esta com|ta com|tem|tinha|apontou|apontando|aponta|ameac\w*|aqui|agora|pegou|"
    r"mostrou|na mao|nas maos|empunhando|com uma|com um|segurando|vai usar|carrega)\b"
)

_PATTERNS: dict[TriageSignal, tuple[re.Pattern[str], ...]] = {
    TriageSignal.SUICIDAL_IDEATION: tuple(
        re.compile(pattern)
        for pattern in (
            # "quero me matar", "quero muito me matar", "penso em me matar"
            rf"\b{_FIRST_PERSON_INTENT}( \w+)? me mat(ar|o)\b",
            r"\bme mato\b",
            r"\b(tirar|acabar com|por fim a|dar fim a|dar fim na) (a )?(minha )?(propria )?vida\b",
            r"\b(quero|queria|vontade de|desejo) morrer\b",
            r"\bnao (quero|aguento|consigo) mais viver\b",
            r"\bsuicid\w*",
            r"\bme (enforcar|jogar (da|de|do|na|no|pela)|cortar)\b",
            r"\b(sumir|desaparecer) (do mundo|para sempre|de vez)\b",
        )
    ),
    TriageSignal.ONGOING_ASSAULT: tuple(
        re.compile(pattern)
        for pattern in (
            rf"\b(esta|estao|ta|tao|continua) me {_ASSAULT_VERB}\b",
            rf"\bme {_ASSAULT_VERB} agora\b",
            r"\b(sendo|estou sendo|to sendo) (agredida|atacada|espancada|estuprada|violentada)\b",
            r"\bsocorro\b",
            r"\b(invadiu|arrombou|esta arrombando|esta forcando) (a )?(porta|casa|minha casa)\b",
        )
    ),
    TriageSignal.DEATH_THREAT: tuple(
        re.compile(pattern)
        for pattern in (
            r"\b(vai|disse que vai|falou que vai|quer|ameacou|ameaca|ameacando|prometeu|"
            r"jurou|disse que ia|falou que ia|vai acabar|ia) (me )?mat(ar|ando)\b",
            rf"\b{_AGGRESSOR}\b.*\bme mat(ar|a|ando)\b",
            r"\b(ameaca|ameacas|ameacou|ameacando|jurou|jurada) de morte\b",
            r"\bmatar (os |meus |nossos |as |minhas )?(filhos|filhas|filho|filha|criancas)\b",
        )
    ),
    TriageSignal.WEAPON_PRESENT: (),
}

_INDETERMINATE_FIXTURE = "frase incerta"
_SIGNAL_LABELS = {
    TriageSignal.SUICIDAL_IDEATION: "ideação suicida",
    TriageSignal.ONGOING_ASSAULT: "agressão em curso",
    TriageSignal.DEATH_THREAT: "ameaça de morte",
    TriageSignal.WEAPON_PRESENT: "presença de arma",
}
_NORMALIZED_INDETERMINATE_FIXTURE = normalize_fixture_sentence(_INDETERMINATE_FIXTURE)


def normalize_for_triage(message: str) -> str:
    """Sem acentos, minúsculas, pontuação como espaço: "Vou ME MATAR!" -> "vou me matar"."""
    decomposed = unicodedata.normalize("NFKD", message)
    without_accents = "".join(c for c in decomposed if unicodedata.category(c) != "Mn")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", without_accents.casefold()).split())


def detect_signals(message: str) -> tuple[TriageSignal, ...]:
    text = normalize_for_triage(message)
    signals = [
        signal
        for signal, patterns in _PATTERNS.items()
        if any(pattern.search(text) for pattern in patterns)
    ]
    if re.search(_WEAPON, text) and re.search(_WEAPON_CONTEXT, text):
        signals.append(TriageSignal.WEAPON_PRESENT)
    return tuple(signals)


class TriageService:
    """Detecta sinais de risco agudo por padrões provisórios; não substitui avaliação real."""

    async def assess(self, message: str) -> TriageResult:
        if not message.strip():
            return TriageResult(status=TriageStatus.NO_ACUTE_SIGNAL)

        signals = detect_signals(message)
        if signals:
            labels = ", ".join(_SIGNAL_LABELS[signal] for signal in signals)
            return TriageResult(
                status=TriageStatus.ACUTE,
                signals=signals,
                guidance=(
                    f"Simulação do protótipo: a mensagem contém sinais de {labels}. "
                    "Nenhuma resposta informativa foi gerada. A detecção é provisória e "
                    "não avalia situações reais. Se precisar de apoio, os contatos úteis "
                    "estão disponíveis nesta tela."
                ),
            )

        if normalize_fixture_sentence(message) == _NORMALIZED_INDETERMINATE_FIXTURE:
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
