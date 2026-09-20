from typing import Any

import pytest

from api.owner_api import OwnerApi
from db.repositories.owner_repository import OwnerRepository
from factories.owner_factory import OwnerFactory


@pytest.mark.smoke
@pytest.mark.positive
@pytest.mark.db
def test_created_owner_is_saved_to_database(
    owner_api: OwnerApi,
    owner_factory: OwnerFactory,
    owner_repository: OwnerRepository,
    created_owner_ids: list[int],
) -> None:
    owner = owner_factory.build()

    response = owner_api.create_owner(owner.to_payload())
    created_owner_ids.append(response.json()["id"])

    assert response.status_code == 201

    stored = owner_repository.get_by_id(response.json()["id"])
    assert stored is not None
    assert stored["first_name"] == owner.first_name
    assert stored["last_name"] == owner.last_name
    assert stored["address"] == owner.address
    assert stored["city"] == owner.city
    assert stored["telephone"] == owner.telephone


@pytest.mark.positive
def test_owner_can_be_read_by_id(owner_api: OwnerApi, created_owner: dict[str, Any]) -> None:
    response = owner_api.get_owner(created_owner["id"])

    assert response.status_code == 200

    stored = response.json()
    assert stored["id"] == created_owner["id"]
    assert stored["firstName"] == created_owner["firstName"]
    assert stored["lastName"] == created_owner["lastName"]
    assert stored["city"] == created_owner["city"]


@pytest.mark.positive
@pytest.mark.db
def test_updated_owner_is_changed_in_database(
    owner_api: OwnerApi,
    owner_factory: OwnerFactory,
    owner_repository: OwnerRepository,
    created_owner: dict[str, Any],
) -> None:
    owner_id = created_owner["id"]
    new_data = owner_factory.build()

    response = owner_api.update_owner(owner_id, new_data.to_payload())

    assert response.status_code == 204

    stored = owner_repository.get_by_id(owner_id)
    assert stored is not None
    assert stored["first_name"] == new_data.first_name
    assert stored["city"] == new_data.city
    assert stored["telephone"] == new_data.telephone


@pytest.mark.positive
@pytest.mark.db
def test_deleted_owner_is_removed_from_database(
    owner_api: OwnerApi,
    owner_repository: OwnerRepository,
    created_owner: dict[str, Any],
) -> None:
    owner_id = created_owner["id"]
    response = owner_api.delete_owner(owner_id)

    assert response.status_code == 204
    assert owner_repository.exists(owner_id) is False


@pytest.mark.positive
def test_owner_can_be_found_by_last_name(
    owner_api: OwnerApi,
    owner_factory: OwnerFactory,
    created_owner_ids: list[int],
) -> None:
    unique_last_name = owner_factory.unique_last_name()
    owner = owner_factory.build(last_name=unique_last_name)

    created = owner_api.create_owner(owner.to_payload())
    created_owner_ids.append(created.json()["id"])

    assert created.status_code == 201

    response = owner_api.get_owners(last_name=unique_last_name)

    assert response.status_code == 200
    found = response.json()
    assert len(found) == 1
    assert found[0]["lastName"] == unique_last_name
