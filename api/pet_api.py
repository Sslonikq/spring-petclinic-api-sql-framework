from typing import Any

from requests import Response

from api.base_client import BaseApiClient


class PetApi:
    RESOURCE = "/api/pets"
    OWNER_RESOURCE = "/api/owners"
    PET_TYPES_RESOURCE = "/api/pettypes"

    def __init__(self, client: BaseApiClient) -> None:
        self._client = client

    def get_pets(self) -> Response:
        return self._client.get(self.RESOURCE)

    def get_pet(self, pet_id: int) -> Response:
        return self._client.get(f"{self.RESOURCE}/{pet_id}")

    def update_pet(self, pet_id: int, payload: dict[str, Any]) -> Response:
        return self._client.put(f"{self.RESOURCE}/{pet_id}", data=payload)

    def delete_pet(self, pet_id: int) -> Response:
        return self._client.delete(f"{self.RESOURCE}/{pet_id}")

    def create_pet(self, owner_id: int, payload: dict[str, Any]) -> Response:
        return self._client.post(f"{self.OWNER_RESOURCE}/{owner_id}/pets", data=payload)

    def get_pet_of_owner(self, owner_id: int, pet_id: int) -> Response:
        return self._client.get(f"{self.OWNER_RESOURCE}/{owner_id}/pets/{pet_id}")

    def update_pet_of_owner(self, owner_id: int, pet_id: int, payload: dict[str, Any]) -> Response:
        return self._client.put(f"{self.OWNER_RESOURCE}/{owner_id}/pets/{pet_id}", data=payload)

    def get_pet_types(self) -> Response:
        return self._client.get(self.PET_TYPES_RESOURCE)
