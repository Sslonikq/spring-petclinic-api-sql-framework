from typing import Any

import pytest

from api.pet_api import PetApi
from db.repositories.pet_repository import PetRepository
from factories.pet_factory import PetFactory

NONEXISTENT_ID = 999999
REQUIRED_FIELDS = ["name", "birthDate", "type"]


@pytest.mark.negative
def test_get_nonexistent_pet_returns_404(pet_api: PetApi) -> None:
    response = pet_api.get_pet(NONEXISTENT_ID)

    assert response.status_code == 404


@pytest.mark.negative
def test_delete_nonexistent_pet_returns_404(pet_api: PetApi) -> None:
    response = pet_api.delete_pet(NONEXISTENT_ID)

    assert response.status_code == 404


@pytest.mark.negative
def test_create_pet_for_nonexistent_owner_returns_404(
    pet_api: PetApi,
    pet_factory: PetFactory,
) -> None:
    response = pet_api.create_pet(NONEXISTENT_ID, pet_factory.build().to_payload())

    assert response.status_code == 404


@pytest.mark.negative
@pytest.mark.parametrize("field", REQUIRED_FIELDS)
def test_create_pet_without_required_field_returns_400(
    pet_api: PetApi,
    pet_factory: PetFactory,
    created_owner: dict[str, Any],
    field: str,
) -> None:
    payload = pet_factory.build().to_payload()
    payload.pop(field)

    response = pet_api.create_pet(created_owner["id"], payload)

    assert response.status_code == 400


@pytest.mark.negative
def test_create_pet_with_type_without_name_returns_400(
    pet_api: PetApi,
    pet_factory: PetFactory,
    created_owner: dict[str, Any],
) -> None:
    payload = pet_factory.build().to_payload()
    payload["type"] = {"id": 2}

    response = pet_api.create_pet(created_owner["id"], payload)

    assert response.status_code == 400


@pytest.mark.negative
def test_create_pet_with_future_birth_date_returns_400(
    pet_api: PetApi,
    pet_factory: PetFactory,
    created_owner: dict[str, Any],
) -> None:
    payload = pet_factory.build().to_payload()
    payload["birthDate"] = "2099-01-01"

    response = pet_api.create_pet(created_owner["id"], payload)

    assert response.status_code == 400


@pytest.mark.negative
def test_create_pet_with_too_long_name_returns_400(
    pet_api: PetApi,
    pet_factory: PetFactory,
    created_owner: dict[str, Any],
) -> None:
    payload = pet_factory.build().to_payload()
    payload["name"] = "a" * 31

    response = pet_api.create_pet(created_owner["id"], payload)

    assert response.status_code == 400


@pytest.mark.negative
@pytest.mark.xfail(
    reason="BUG: пустое имя питомца возвращает 500 вместо 400",
    raises=AssertionError,
    strict=True,
)
def test_create_pet_with_empty_name_returns_400(
    pet_api: PetApi,
    pet_factory: PetFactory,
    created_owner: dict[str, Any],
) -> None:
    payload = pet_factory.build().to_payload()
    payload["name"] = ""

    response = pet_api.create_pet(created_owner["id"], payload)

    assert response.status_code == 400


@pytest.mark.negative
@pytest.mark.xfail(
    reason="BUG: неверный формат даты возвращает 500 вместо 400",
    raises=AssertionError,
    strict=True,
)
def test_create_pet_with_invalid_date_format_returns_400(
    pet_api: PetApi,
    pet_factory: PetFactory,
    created_owner: dict[str, Any],
) -> None:
    payload = pet_factory.build().to_payload()
    payload["birthDate"] = "17.05.2020"

    response = pet_api.create_pet(created_owner["id"], payload)

    assert response.status_code == 400


@pytest.mark.negative
@pytest.mark.db
def test_invalid_pet_is_not_saved_to_database(
    pet_api: PetApi,
    pet_factory: PetFactory,
    pet_repository: PetRepository,
    created_owner: dict[str, Any],
) -> None:
    payload = pet_factory.build().to_payload()
    payload["birthDate"] = "2099-01-01"

    response = pet_api.create_pet(created_owner["id"], payload)

    assert response.status_code == 400
    assert pet_repository.get_by_owner_id(created_owner["id"]) == []
