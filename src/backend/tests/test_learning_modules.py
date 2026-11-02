import asyncio

import pytest
from fastapi.testclient import TestClient

from aurora_backend.contexts.accounts.services.accounts.models import (
    InvalidModuleProgressError,
)
from aurora_backend.contexts.accounts.services.accounts.service import AccountService
from aurora_backend.contexts.learning.services.modules.service import ModuleCatalogService
from aurora_backend.main import create_app
from aurora_backend.shared.legal_sources import MARIA_DA_PENHA_ART_7_II

PASSWORD = "senhaforte1"


def run(coroutine):
    return asyncio.run(coroutine)


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app(account_service=AccountService()))


def test_catalog_lists_backlog_topics_with_one_ready_module() -> None:
    modules = run(ModuleCatalogService().list_modules())

    assert [module.id for module in modules][:2] == [
        "o-que-e-violencia-psicologica",
        "ciclo-do-abuso",
    ]
    ready = [module for module in modules if not module.in_preparation]
    assert [module.id for module in ready] == ["o-que-e-violencia-psicologica"]
    assert all(module.demo for module in modules)


def test_ready_module_quotes_approved_legal_sources_literally() -> None:
    module = run(ModuleCatalogService().get_module("o-que-e-violencia-psicologica"))

    assert MARIA_DA_PENHA_ART_7_II.text in module.sections[0].paragraphs[0]
    assert module.sections[0].source is not None
    assert module.sections[0].source.url.startswith("https://www.planalto.gov.br/")


def test_placeholder_modules_make_no_content_claims() -> None:
    module = run(ModuleCatalogService().get_module("ciclo-do-abuso"))

    assert module.in_preparation is True
    assert all(
        paragraph.startswith("Conteúdo em preparação — demonstração")
        for section in module.sections
        for paragraph in section.paragraphs
    )


def test_progress_is_saved_and_completion_is_kept_when_reviewing() -> None:
    service = AccountService()
    session = run(service.register("lua_azul", PASSWORD))

    run(service.save_module_progress(session.token, "ciclo-do-abuso", 1, False))
    run(service.save_module_progress(session.token, "ciclo-do-abuso", 1, True))
    reviewed = run(service.save_module_progress(session.token, "ciclo-do-abuso", 0, False))

    assert reviewed.completed is True
    assert run(service.list_module_progress(session.token)) == (reviewed,)


@pytest.mark.parametrize(
    ("module_id", "section"), [("Ciclo Do Abuso", 0), ("x" * 61, 0), ("ok", 50)]
)
def test_invalid_progress_is_rejected(module_id: str, section: int) -> None:
    service = AccountService()
    session = run(service.register("lua_azul", PASSWORD))
    with pytest.raises(InvalidModuleProgressError):
        run(service.save_module_progress(session.token, module_id, section, False))


def test_progress_is_deleted_with_account() -> None:
    service = AccountService()
    session = run(service.register("lua_azul", PASSWORD))
    run(service.save_module_progress(session.token, "ciclo-do-abuso", 1, True))
    run(service.delete_account(session.token))

    new_session = run(service.register("lua_azul", PASSWORD))
    assert run(service.list_module_progress(new_session.token)) == ()


def test_http_modules_and_progress(client: TestClient) -> None:
    listing = client.get("/api/learning/modules").json()["modules"]
    assert listing[0]["section_count"] == 2
    detail = client.get("/api/learning/modules/o-que-e-violencia-psicologica").json()
    assert detail["sections"][1]["source"]["locator"] == "art. 147-B"
    assert client.get("/api/learning/modules/inexistente").status_code == 404

    token = client.post(
        "/api/accounts", json={"nickname": "lua_azul", "password": PASSWORD}
    ).json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    saved = client.put(
        "/api/account/module-progress/gaslighting",
        json={"section": 1, "completed": False},
        headers=headers,
    )
    assert saved.json() == {"module_id": "gaslighting", "section": 1, "completed": False}
    assert client.get("/api/account/module-progress", headers=headers).json()["progress"] == [
        saved.json()
    ]
    assert client.get("/api/account/module-progress").status_code == 401
    assert (
        client.put(
            "/api/account/module-progress/gaslighting",
            json={"section": -1, "completed": False},
            headers=headers,
        ).status_code
        == 422
    )
