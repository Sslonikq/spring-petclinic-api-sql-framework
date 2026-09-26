from typing import Any

from requests import Response

from api.base_client import BaseApiClient


class VisitApi:
    RESOURCE = "/api/visits"
    OWNER_RESOURCE = "/api/owners"

    def __init__(self, client: BaseApiClient) -> None:
        self._client = client

    def create_visit(self, owner_id: int, pet_id: int, payload: dict[str, Any]) -> Response:
        return self._client.post(
            f"{self.OWNER_RESOURCE}/{owner_id}/pets/{pet_id}/visits",
            data=payload,
        )

    def get_visits(self) -> Response:
        return self._client.get(self.RESOURCE)

    def get_visit(self, visit_id: int) -> Response:
        return self._client.get(f"{self.RESOURCE}/{visit_id}")

    def update_visit(self, visit_id: int, payload: dict[str, Any]) -> Response:
        return self._client.put(f"{self.RESOURCE}/{visit_id}", data=payload)

    def delete_visit(self, visit_id: int) -> Response:
        return self._client.delete(f"{self.RESOURCE}/{visit_id}")
