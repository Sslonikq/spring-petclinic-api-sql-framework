import pytest

from api.owner_api import OwnerApi
from db.repositories.owner_repository import OwnerRepository
from factories.owner_factory import OwnerFactory

NONEXISTENT_OWNER_ID = 999999
REQUIRED_FIELDS = ["firstName", "lastName", "address", "city", "telephone"]


@pytest.mark.negative
def test_get_nonexistent_owner_returns_404(owner_api: OwnerApi) -> None:
    response = owner_api.get_owner(NONEXISTENT_OWNER_ID)

    assert response.status_code == 404


@pytest.mark.negative
def test_delete_nonexistent_owner_returns_404(owner_api: OwnerApi) -> None:
    response = owner_api.delete_owner(NONEXISTENT_OWNER_ID)

    assert response.status_code == 404


@pytest.mark.negative
@pytest.mark.parametrize("field", REQUIRED_FIELDS)
def test_create_owner_without_required_field_returns_400(
    owner_api: OwnerApi,
    owner_factory: OwnerFactory,
    field: str,
) -> None:
    payload = owner_factory.build().to_payload()
    payload.pop(field)

    response = owner_api.create_owner(payload)

    assert response.status_code == 400


@pytest.mark.negative
@pytest.mark.parametrize("field", REQUIRED_FIELDS)
def test_create_owner_with_empty_required_field_returns_400(
    owner_api: OwnerApi,
    owner_factory: OwnerFactory,
    field: str,
) -> None:
    payload = owner_factory.build().to_payload()
    payload[field] = ""

    response = owner_api.create_owner(payload)

    assert response.status_code == 400


@pytest.mark.negative
def test_create_owner_with_digits_in_last_name_returns_400(
    owner_api: OwnerApi,
    owner_factory: OwnerFactory,
) -> None:
    payload = owner_factory.build().to_payload()
    payload["lastName"] = "123"

    response = owner_api.create_owner(payload)

    assert response.status_code == 400


@pytest.mark.negative
def test_create_owner_with_too_long_first_name_returns_400(
    owner_api: OwnerApi,
    owner_factory: OwnerFactory,
) -> None:
    payload = owner_factory.build().to_payload()
    payload["firstName"] = "a" * 31

    response = owner_api.create_owner(payload)

    assert response.status_code == 400


@pytest.mark.negative
@pytest.mark.xfail(reason="BUG: невалидный телефон возвращает 500 вместо 400", strict=True)
def test_create_owner_with_short_telephone_returns_400(
    owner_api: OwnerApi,
    owner_factory: OwnerFactory,
) -> None:
    payload = owner_factory.build().to_payload()
    payload["telephone"] = "123"

    response = owner_api.create_owner(payload)

    assert response.status_code == 400


@pytest.mark.negative
@pytest.mark.db
def test_invalid_owner_is_not_saved_to_database(
    owner_api: OwnerApi,
    owner_factory: OwnerFactory,
    owner_repository: OwnerRepository,
) -> None:
    unique_last_name = owner_factory.unique_last_name()
    payload = owner_factory.build(last_name=unique_last_name).to_payload()
    payload["firstName"] = ""

    response = owner_api.create_owner(payload)

    assert response.status_code == 400
    assert owner_repository.get_by_last_name(unique_last_name) == []
