import asyncio

import pytest
from fastapi.testclient import TestClient

from aurora_backend.contexts.questionnaire.services.questionnaire.models import (
    DemoBand,
    InvalidAnswersError,
)
from aurora_backend.contexts.questionnaire.services.questionnaire.service import (
    QuestionnaireService,
)
from aurora_backend.main import create_app

QUESTIONS = "/api/questionnaire/questions"
RESULTS = "/api/questionnaire/results"


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


def evaluate(answers: dict[str, str]):
    return asyncio.run(QuestionnaireService().evaluate(answers))


def test_questions_are_demo_placeholders_plus_backlog_help_type(client: TestClient) -> None:
    response = client.get(QUESTIONS)

    assert response.status_code == 200
    payload = response.json()
    assert payload["demo"] is True
    assert [question["id"] for question in payload["questions"]] == [
        "demo_1",
        "demo_2",
        "help_type",
    ]
    assert payload["questions"][0]["title"] == "Pergunta de demonstração 1"
    help_labels = [option["label"] for option in payload["questions"][2]["options"]]
    assert help_labels == [
        "Denúncia",
        "Orientação jurídica",
        "Apoio psicológico",
        "Apoio entre pares",
        "Prefiro não responder",
    ]
    for question in payload["questions"]:
        assert question["options"][-1] == {"id": "skip", "label": "Prefiro não responder"}


@pytest.mark.parametrize(
    ("demo_1", "demo_2", "band"),
    [
        ("a", "a", DemoBand.A),
        ("a", "b", DemoBand.B),
        ("skip", "a", DemoBand.B),
        ("b", "b", DemoBand.C),
        ("skip", "skip", DemoBand.C),
    ],
)
def test_demo_band_counts_option_a(demo_1: str, demo_2: str, band: DemoBand) -> None:
    result = evaluate({"demo_1": demo_1, "demo_2": demo_2, "help_type": "legal"})

    assert result.band is band
    assert result.help_type == "legal"
    assert result.demo is True


def test_skipped_help_type_returns_none() -> None:
    assert evaluate({"demo_1": "a", "demo_2": "a", "help_type": "skip"}).help_type is None


@pytest.mark.parametrize(
    "answers",
    [
        {"demo_1": "a", "demo_2": "a"},
        {"demo_1": "a", "demo_2": "a", "help_type": "legal", "extra": "a"},
        {"demo_1": "z", "demo_2": "a", "help_type": "legal"},
        {"demo_1": "a", "demo_2": "a", "help_type": "a"},
    ],
)
def test_invalid_answers_are_rejected(answers: dict[str, str]) -> None:
    with pytest.raises(InvalidAnswersError):
        evaluate(answers)


def test_results_endpoint_returns_band_and_help_type(client: TestClient) -> None:
    response = client.post(
        RESULTS,
        json={"answers": {"demo_1": "a", "demo_2": "b", "help_type": "psychological"}},
    )

    assert response.status_code == 200
    assert response.json() == {"band": "B", "help_type": "psychological", "demo": True}


def test_results_endpoint_rejects_incomplete_answers(client: TestClient) -> None:
    response = client.post(RESULTS, json={"answers": {"demo_1": "a"}})

    assert response.status_code == 422
