from typing import Any

import pytest

from api.pet_api import PetApi
from db.repositories.pet_repository import PetRepository
from factories.pet_factory import PetFactory
from models.pet import PetType


@pytest.mark.smoke
@pytest.mark.positive
@pytest.mark.db
def test_created_pet_is_saved_to_database(
    pet_api: PetApi,
    pet_factory: PetFactory,
    pet_repository: PetRepository,
    created_owner: dict[str, Any],
    created_pet_ids: list[int],
) -> None:
    pet = pet_factory.build()

    response = pet_api.create_pet(created_owner["id"], pet.to_payload())
    created_pet_ids.append(response.json()["id"])

    assert response.status_code == 201

    stored = pet_repository.get_by_id(response.json()["id"])
    assert stored is not None
    assert stored["name"] == pet.name
    assert stored["birth_date"] == pet.birth_date
    assert stored["type_id"] == pet.type.id


@pytest.mark.positive
@pytest.mark.db
def test_pet_is_linked_to_owner(
    pet_repository: PetRepository,
    created_owner: dict[str, Any],
    created_pet: dict[str, Any],
) -> None:
    stored = pet_repository.get_by_id(created_pet["id"])

    assert stored is not None
    assert stored["owner_id"] == created_owner["id"]


@pytest.mark.positive
@pytest.mark.db
def test_pet_type_is_saved_correctly(
    pet_api: PetApi,
    pet_factory: PetFactory,
    pet_repository: PetRepository,
    created_owner: dict[str, Any],
    created_pet_ids: list[int],
) -> None:
    pet = pet_factory.build(type=PetType(id=4, name="snake"))

    response = pet_api.create_pet(created_owner["id"], pet.to_payload())
    created_pet_ids.append(response.json()["id"])

    assert response.status_code == 201

    stored = pet_repository.get_with_type(response.json()["id"])
    assert stored is not None
    assert stored["type_id"] == 4
    assert stored["type_name"] == "snake"


@pytest.mark.positive
def test_pet_can_be_read_by_id(pet_api: PetApi, created_pet: dict[str, Any]) -> None:
    response = pet_api.get_pet(created_pet["id"])

    assert response.status_code == 200

    body = response.json()
    assert body["id"] == created_pet["id"]
    assert body["name"] == created_pet["name"]
    assert body["ownerId"] == created_pet["ownerId"]


@pytest.mark.positive
@pytest.mark.db
def test_updated_pet_is_changed_in_database(
    pet_api: PetApi,
    pet_factory: PetFactory,
    pet_repository: PetRepository,
    created_pet: dict[str, Any],
) -> None:
    new_data = pet_factory.build()

    response = pet_api.update_pet(created_pet["id"], new_data.to_payload())

    assert response.status_code == 204

    stored = pet_repository.get_by_id(created_pet["id"])
    assert stored is not None
    assert stored["name"] == new_data.name
    assert stored["birth_date"] == new_data.birth_date


@pytest.mark.positive
@pytest.mark.db
def test_deleted_pet_is_removed_from_database(
    pet_api: PetApi,
    pet_repository: PetRepository,
    created_pet: dict[str, Any],
) -> None:
    response = pet_api.delete_pet(created_pet["id"])

    assert response.status_code == 204
    assert pet_repository.exists(created_pet["id"]) is False


@pytest.mark.positive
@pytest.mark.db
def test_owner_pets_are_stored_in_database(
    pet_repository: PetRepository,
    created_pet: dict[str, Any],
    created_owner: dict[str, Any],
) -> None:
    pets = pet_repository.get_by_owner_id(created_owner["id"])

    assert len(pets) == 1
    assert pets[0]["id"] == created_pet["id"]
