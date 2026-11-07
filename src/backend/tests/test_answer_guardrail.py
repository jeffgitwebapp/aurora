"""Guardrail de saída (plano §5.5): respostas violadoras sintéticas nunca passam (CA-03 M4)."""

import pytest

from aurora_backend.contexts.conversation.services.answer_guardrail.service import (
    AnswerGuardrailService,
    AnswerSegment,
)

ALLOWED_IDS = frozenset({"cp-art147b#caput", "lei-11340-2006#art7-II"})
ALLOWED_URLS = frozenset({"https://www.planalto.gov.br/ccivil_03/decreto-lei/del2848compilado.htm"})
CITED = ("cp-art147b#caput",)


def check(*segments: AnswerSegment):
    return AnswerGuardrailService().check(
        segments, allowed_source_ids=ALLOWED_IDS, allowed_urls=ALLOWED_URLS
    )


def test_grounded_answer_with_limit_segment_passes() -> None:
    result = check(
        AnswerSegment(
            "Desde 2021, causar dano emocional à mulher é crime, com pena de 6 meses a 2 anos.",
            CITED,
        ),
        AnswerSegment(
            "Eu não avalio a sua situação. Os contatos úteis, como o 180, estão na tela.",
            (),
        ),
    )

    assert result.passed, result.violations


VIOLATIONS = [
    ("no_citation", [AnswerSegment("Violência psicológica é muito comum.", ())]),
    ("empty_answer", []),
    ("unknown_source_id", [AnswerSegment("Isso está na lei.", ("inventado#1",))]),
    ("uncited_fact", [AnswerSegment("A pena é de 10 anos.", ()), AnswerSegment("ok", CITED)]),
    ("diagnosis", [AnswerSegment("Pelo que você conta, você tem depressão.", CITED)]),
    ("diagnosis", [AnswerSegment("Voce esta com ansiedade.", CITED)]),
    ("diagnosis", [AnswerSegment("Seu marido é um psicopata.", CITED)]),
    ("prescription", [AnswerSegment("Tome um calmante para dormir.", CITED)]),
    ("prescription", [AnswerSegment("Use fluoxetina 20 mg.", CITED)]),
    ("coercive_decision", [AnswerSegment("Você deve denunciar hoje mesmo.", CITED)]),
    ("coercive_decision", [AnswerSegment("Saia de casa agora.", CITED)]),
    ("coercive_decision", [AnswerSegment("Você precisa se separar dele.", CITED)]),
    ("individual_legal_opinion", [AnswerSegment("No seu caso, isso é crime.", CITED)]),
    ("individual_legal_opinion", [AnswerSegment("Ele vai ser preso se você denunciar.", CITED)]),
    ("individual_legal_opinion", [AnswerSegment("O que ele fez com você é crime.", CITED)]),
    ("acts_on_behalf", [AnswerSegment("Já acionei a delegacia para você.", CITED)]),
    ("acts_on_behalf", [AnswerSegment("Encaminhei seu caso para a Defensoria.", CITED)]),
    ("unauthorized_contact", [AnswerSegment("Ligue para (81) 3333-4444.", CITED)]),
    ("unauthorized_contact", [AnswerSegment("WhatsApp 61 99999-0000.", CITED)]),
    ("unauthorized_contact", [AnswerSegment("Disque 100 para denunciar.", CITED)]),
    ("unauthorized_contact", [AnswerSegment("Ligue para o número 181.", CITED)]),
    ("unauthorized_contact", [AnswerSegment("Telefone da delegacia: 3333-4444.", CITED)]),
    ("unauthorized_link", [AnswerSegment("Veja https://site-qualquer.com/ajuda.", CITED)]),
    ("unauthorized_link", [AnswerSegment("Acesse www.exemplo.com.", CITED)]),
]


@pytest.mark.parametrize(("violation", "segments"), VIOLATIONS)
def test_synthetic_violations_never_pass(violation: str, segments: list[AnswerSegment]) -> None:
    result = check(*segments)

    assert not result.passed
    assert violation in result.violations


def test_link_from_provided_source_is_allowed() -> None:
    url = next(iter(ALLOWED_URLS))

    assert check(AnswerSegment(f"Veja o texto completo em {url}.", CITED)).passed


def test_emergency_numbers_are_allowed() -> None:
    assert check(AnswerSegment("Se precisar, o 190 e o 180 estão na tela.", CITED)).passed


def test_legal_article_numbers_in_cited_segment_are_not_contacts() -> None:
    assert check(AnswerSegment("O art. 147-B foi incluído pela Lei 14.188/2021.", CITED)).passed


def test_law_numbers_with_dots_and_slashes_are_not_phones() -> None:
    segment = AnswerSegment(
        "A Lei 13.104/2015 e a Lei 14.188/2021 alteraram o Código Penal.", CITED
    )

    assert check(segment).passed
