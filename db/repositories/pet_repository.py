from typing import Any

from db.client import DatabaseClient


class PetRepository:
    def __init__(self, client: DatabaseClient) -> None:
        self._client = client

    def get_by_id(self, pet_id: int) -> dict[str, Any] | None:
        return self._client.fetch_one("SELECT * FROM pets WHERE id = %s", (pet_id,))

    def get_by_owner_id(self, owner_id: int) -> list[dict[str, Any]]:
        return self._client.fetch_all(
            "SELECT * FROM pets WHERE owner_id = %s ORDER BY id",
            (owner_id,),
        )

    def get_with_type(self, pet_id: int) -> dict[str, Any] | None:
        return self._client.fetch_one(
            """
            SELECT p.id, p.name, p.birth_date, p.owner_id, p.type_id, t.name AS type_name
            FROM pets p
            JOIN types t ON t.id = p.type_id
            WHERE p.id = %s
            """,
            (pet_id,),
        )

    def exists(self, pet_id: int) -> bool:
        return self.get_by_id(pet_id) is not None

    def delete_by_id(self, pet_id: int) -> int:
        return self._client.execute("DELETE FROM pets WHERE id = %s", (pet_id,))
