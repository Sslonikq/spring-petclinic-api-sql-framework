from collections.abc import Iterator
from typing import Any

import pytest

from api.base_client import BaseApiClient
from api.owner_api import OwnerApi
from db.client import DatabaseClient
from db.repositories.owner_repository import OwnerRepository
from factories.owner_factory import OwnerFactory


@pytest.fixture(scope="session")
def api_client() -> Iterator[BaseApiClient]:
    client = BaseApiClient()
    yield client
    client.close()


@pytest.fixture(scope="session")
def db_client() -> Iterator[DatabaseClient]:
    client = DatabaseClient()
    yield client
    client.close()


@pytest.fixture
def owner_api(api_client: BaseApiClient) -> OwnerApi:
    return OwnerApi(api_client)


@pytest.fixture
def owner_repository(db_client: DatabaseClient) -> OwnerRepository:
    return OwnerRepository(db_client)


@pytest.fixture
def owner_factory() -> OwnerFactory:
    return OwnerFactory()


@pytest.fixture
def created_owner_ids(owner_repository: OwnerRepository) -> Iterator[list[int]]:
    owner_ids: list[int] = []
    yield owner_ids
    for owner_id in owner_ids:
        owner_repository.delete_by_id(owner_id)


@pytest.fixture
def created_owner(
    owner_api: OwnerApi,
    owner_factory: OwnerFactory,
    created_owner_ids: list[int],
) -> dict[str, Any]:
    owner = owner_factory.build()
    response = owner_api.create_owner(owner.to_payload())
    response.raise_for_status()

    created: dict[str, Any] = response.json()
    created_owner_ids.append(created["id"])
    return created
