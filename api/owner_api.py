from typing import Any

from requests import Response

from api.base_client import BaseApiClient


class OwnerApi:
    RESOURCE = "/api/owners"

    def __init__(self, client: BaseApiClient) -> None:
        self._client = client

    def get_owners(self, last_name: str | None = None) -> Response:
        params = {"lastName": last_name} if last_name else None
        return self._client.get(self.RESOURCE, params=params)

    def get_owner(self, owner_id: int) -> Response:
        return self._client.get(f"{self.RESOURCE}/{owner_id}")

    def create_owner(self, payload: dict[str, Any]) -> Response:
        return self._client.post(self.RESOURCE, data=payload)

    def update_owner(self, owner_id: int, payload: dict[str, Any]) -> Response:
        return self._client.put(f"{self.RESOURCE}/{owner_id}", data=payload)

    def delete_owner(self, owner_id: int) -> Response:
        return self._client.delete(f"{self.RESOURCE}/{owner_id}")
