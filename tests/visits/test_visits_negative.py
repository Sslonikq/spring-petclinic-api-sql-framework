from typing import Any

import pytest

from api.visit_api import VisitApi
from db.repositories.visit_repository import VisitRepository
from factories.visit_factory import VisitFactory

NONEXISTENT_ID = 999999


@pytest.mark.negative
def test_get_nonexistent_visit_returns_404(visit_api: VisitApi) -> None:
    response = visit_api.get_visit(NONEXISTENT_ID)

    assert response.status_code == 404


@pytest.mark.negative
def test_update_nonexistent_visit_returns_404(
    visit_api: VisitApi,
    visit_factory: VisitFactory,
) -> None:
    response = visit_api.update_visit(NONEXISTENT_ID, visit_factory.build().to_payload())

    assert response.status_code == 404


@pytest.mark.negative
def test_delete_nonexistent_visit_returns_404(visit_api: VisitApi) -> None:
    response = visit_api.delete_visit(NONEXISTENT_ID)

    assert response.status_code == 404


@pytest.mark.negative
def test_create_visit_without_description_returns_400(
    visit_api: VisitApi,
    visit_factory: VisitFactory,
    created_owner: dict[str, Any],
    created_pet: dict[str, Any],
) -> None:
    payload = visit_factory.build().to_payload()
    payload.pop("description")

    response = visit_api.create_visit(created_owner["id"], created_pet["id"], payload)

    assert response.status_code == 400


@pytest.mark.negative
def test_create_visit_with_empty_description_returns_400(
    visit_api: VisitApi,
    visit_factory: VisitFactory,
    created_owner: dict[str, Any],
    created_pet: dict[str, Any],
) -> None:
    payload = visit_factory.build().to_payload()
    payload["description"] = ""

    response = visit_api.create_visit(created_owner["id"], created_pet["id"], payload)

    assert response.status_code == 400


@pytest.mark.negative
def test_create_visit_with_too_long_description_returns_400(
    visit_api: VisitApi,
    visit_factory: VisitFactory,
    created_owner: dict[str, Any],
    created_pet: dict[str, Any],
) -> None:
    payload = visit_factory.build().to_payload()
    payload["description"] = "a" * 256

    response = visit_api.create_visit(created_owner["id"], created_pet["id"], payload)

    assert response.status_code == 400


@pytest.mark.negative
def test_create_visit_for_nonexistent_pet_returns_404(
    visit_api: VisitApi,
    visit_factory: VisitFactory,
    created_owner: dict[str, Any],
) -> None:
    response = visit_api.create_visit(
        created_owner["id"],
        NONEXISTENT_ID,
        visit_factory.build().to_payload(),
    )

    assert response.status_code == 404


@pytest.mark.negative
@pytest.mark.xfail(
    reason="BUG: неверный формат даты визита возвращает 500 вместо 400",
    raises=AssertionError,
    strict=True,
)
def test_create_visit_with_invalid_date_format_returns_400(
    visit_api: VisitApi,
    visit_factory: VisitFactory,
    created_owner: dict[str, Any],
    created_pet: dict[str, Any],
) -> None:
    payload = visit_factory.build().to_payload()
    payload["date"] = "10.05.2024"

    response = visit_api.create_visit(created_owner["id"], created_pet["id"], payload)

    assert response.status_code == 400


@pytest.mark.negative
@pytest.mark.xfail(
    reason="BUG: владелец в URL не проверяется, визит создаётся с 201 вместо 404",
    raises=AssertionError,
    strict=True,
)
def test_create_visit_with_nonexistent_owner_returns_404(
    visit_api: VisitApi,
    visit_factory: VisitFactory,
    created_pet: dict[str, Any],
    created_visit_ids: list[int],
) -> None:
    response = visit_api.create_visit(
        NONEXISTENT_ID,
        created_pet["id"],
        visit_factory.build().to_payload(),
    )
    if response.status_code == 201:
        created_visit_ids.append(response.json()["id"])

    assert response.status_code == 404


@pytest.mark.negative
@pytest.mark.db
def test_invalid_visit_is_not_saved_to_database(
    visit_api: VisitApi,
    visit_factory: VisitFactory,
    visit_repository: VisitRepository,
    created_owner: dict[str, Any],
    created_pet: dict[str, Any],
) -> None:
    payload = visit_factory.build().to_payload()
    payload["description"] = ""

    response = visit_api.create_visit(created_owner["id"], created_pet["id"], payload)

    assert response.status_code == 400
    assert visit_repository.get_by_pet_id(created_pet["id"]) == []
