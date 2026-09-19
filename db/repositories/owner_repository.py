from typing import Any

from db.client import DatabaseClient


class OwnerRepository:
    def __init__(self, client: DatabaseClient) -> None:
        self._client = client

    def get_by_id(self, owner_id: int) -> dict[str, Any] | None:
        return self._client.fetch_one("SELECT * FROM owners WHERE id = %s", (owner_id,))

    def get_by_last_name(self, last_name: str) -> list[dict[str, Any]]:
        return self._client.fetch_all(
            "SELECT * FROM owners WHERE last_name = %s ORDER BY id",
            (last_name,),
        )

    def count(self) -> int:
        row = self._client.fetch_one("SELECT count(*) AS total FROM owners")
        return row["total"]

    def exists(self, owner_id: int) -> bool:
        return self.get_by_id(owner_id) is not None

    def delete_by_id(self, owner_id: int) -> int:
        return self._client.execute("DELETE FROM owners WHERE id = %s", (owner_id,))
