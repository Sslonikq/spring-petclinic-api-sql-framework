from typing import Any

import pytest

from api.pet_api import PetApi
from api.visit_api import VisitApi
from db.repositories.visit_repository import VisitRepository
from factories.visit_factory import VisitFactory


@pytest.mark.smoke
@pytest.mark.positive
@pytest.mark.db
def test_created_visit_is_saved_to_database(
    visit_api: VisitApi,
    visit_factory: VisitFactory,
    visit_repository: VisitRepository,
    created_owner: dict[str, Any],
    created_pet: dict[str, Any],
    created_visit_ids: list[int],
) -> None:
    visit = visit_factory.build()

    response = visit_api.create_visit(created_owner["id"], created_pet["id"], visit.to_payload())
    created_visit_ids.append(response.json()["id"])

    assert response.status_code == 201

    stored = visit_repository.get_by_id(response.json()["id"])
    assert stored is not None
    assert stored["description"] == visit.description
    assert stored["visit_date"] == visit.date


@pytest.mark.positive
@pytest.mark.db
def test_visit_is_linked_to_pet(
    visit_repository: VisitRepository,
    created_visit: dict[str, Any],
    created_pet: dict[str, Any],
) -> None:
    stored = visit_repository.get_by_id(created_visit["id"])

    assert stored is not None
    assert stored["pet_id"] == created_pet["id"]


@pytest.mark.positive
def test_visit_can_be_read_by_id(visit_api: VisitApi, created_visit: dict[str, Any]) -> None:
    response = visit_api.get_visit(created_visit["id"])

    assert response.status_code == 200

    body = response.json()
    assert body["id"] == created_visit["id"]
    assert body["description"] == created_visit["description"]
    assert body["petId"] == created_visit["petId"]
    assert body["date"] == created_visit["date"]


@pytest.mark.positive
@pytest.mark.db
def test_updated_visit_is_changed_in_database(
    visit_api: VisitApi,
    visit_factory: VisitFactory,
    visit_repository: VisitRepository,
    created_visit: dict[str, Any],
) -> None:
    new_visit = visit_factory.build()

    response = visit_api.update_visit(created_visit["id"], new_visit.to_payload())

    assert response.status_code == 204

    stored = visit_repository.get_by_id(created_visit["id"])
    assert stored is not None
    assert stored["description"] == new_visit.description
    assert stored["visit_date"] == new_visit.date


@pytest.mark.positive
@pytest.mark.db
def test_deleted_visit_is_removed_from_database(
    visit_api: VisitApi,
    visit_repository: VisitRepository,
    created_visit: dict[str, Any],
) -> None:
    response = visit_api.delete_visit(created_visit["id"])

    assert response.status_code == 204
    assert visit_repository.exists(created_visit["id"]) is False


@pytest.mark.positive
@pytest.mark.db
def test_visit_without_date_is_saved_with_null_date(
    visit_api: VisitApi,
    visit_factory: VisitFactory,
    visit_repository: VisitRepository,
    created_owner: dict[str, Any],
    created_pet: dict[str, Any],
    created_visit_ids: list[int],
) -> None:
    visit = visit_factory.build(date=None)

    response = visit_api.create_visit(created_owner["id"], created_pet["id"], visit.to_payload())
    created_visit_ids.append(response.json()["id"])

    assert response.status_code == 201

    stored = visit_repository.get_by_id(response.json()["id"])
    assert stored is not None
    assert stored["visit_date"] is None


@pytest.mark.positive
@pytest.mark.db
def test_deleting_pet_removes_its_visits(
    pet_api: PetApi,
    visit_repository: VisitRepository,
    created_visit: dict[str, Any],
    created_pet: dict[str, Any],
) -> None:
    response = pet_api.delete_pet(created_pet["id"])

    assert response.status_code == 204
    assert visit_repository.exists(created_visit["id"]) is False
    assert visit_repository.get_by_pet_id(created_pet["id"]) == []
