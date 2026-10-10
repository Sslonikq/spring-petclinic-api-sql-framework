from typing import Any

import pytest

from api.owner_api import OwnerApi
from api.pet_api import PetApi
from api.visit_api import VisitApi
from db.repositories.owner_repository import OwnerRepository
from db.repositories.pet_repository import PetRepository
from db.repositories.visit_repository import VisitRepository
from factories.owner_factory import OwnerFactory
from factories.pet_factory import PetFactory
from factories.visit_factory import VisitFactory
from models.pet import PetType


@pytest.mark.integration
@pytest.mark.db
def test_owner_pet_visit_chain_is_consistent_in_database(
    owner_api: OwnerApi,
    pet_api: PetApi,
    visit_api: VisitApi,
    owner_repository: OwnerRepository,
    owner_factory: OwnerFactory,
    pet_repository: PetRepository,
    visit_repository: VisitRepository,
    created_owner_ids: list[int],
    created_pet_ids: list[int],
    created_visit_ids: list[int],
) -> None:
    owner = owner_factory.build()
    owner_response = owner_api.create_owner(owner.to_payload())
    owner_id = owner_response.json()["id"]
    created_owner_ids.append(owner_id)
    assert owner_response.status_code == 201

    pet = PetFactory.build(type = PetType(id=4, name="snake"))
    pet_response = pet_api.create_pet(owner_id, pet.to_payload())
    pet_id = pet_response.json()["id"]
    created_pet_ids.append(pet_id)
    assert pet_response.status_code == 201

    visit = VisitFactory.build()
    visit_response = visit_api.create_visit(owner_id, pet_id, visit.to_payload())
    visit_id = visit_response.json()["id"]
    created_visit_ids.append(visit_id)
    assert visit_response.status_code == 201

    chain = visit_repository.get_full_chain(visit_id)
    assert chain is not None

    assert chain["owner_id"] == owner_id
    assert chain["last_name"] == owner.last_name
    assert chain["pet_id"] == pet_id
    assert chain["pet_name"] == pet.name
    assert chain["pet_type"] == "snake"
    assert chain["description"] == visit.description
    assert chain["visit_date"] == visit.date



@pytest.mark.integration
@pytest.mark.db
def test_owner_response_contains_pet_and_visit(
    owner_api: OwnerApi,
    created_owner: dict[str, Any],
    created_pet: dict[str, Any],
    created_visit: dict[str, Any],
) -> None:
    response = owner_api.get_owner(created_owner["id"])
    assert response.status_code == 200

    pets = response.json()["pets"]
    assert len(pets) == 1
    assert pets[0]["id"] == created_pet["id"]
    visits = pets[0]["visits"]
    assert len(visits) == 1
    assert visits[0]["id"] == created_visit["id"]



@pytest.mark.integration
@pytest.mark.db
def test_owner_with_pets_is_not_deleted(
    owner_api: OwnerApi,
    owner_repository: OwnerRepository,
    pet_repository: PetRepository,
    visit_repository: VisitRepository,
    created_owner: dict[str, Any],
    created_pet: dict[str, Any],
    created_visit: dict[str, Any],
) -> None:
    owner_api.delete_owner(created_owner["id"])

    assert owner_repository.exists(created_owner["id"]) is True
    assert pet_repository.exists(created_pet["id"]) is True
    assert visit_repository.exists(created_visit["id"]) is True



@pytest.mark.integration
@pytest.mark.xfail(
    reason="BUG: удаление владельца с питомцами возвращает 404 вместо 409",
    raises=AssertionError,
    strict=True,
)
def test_deleting_owner_with_pets_returns_409(
    owner_api: OwnerApi,
    created_owner: dict[str, Any],
    created_visit: dict[str, Any],
) -> None:
    response = owner_api.delete_owner(created_owner["id"])

    assert response.status_code == 409
