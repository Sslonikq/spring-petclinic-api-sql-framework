from typing import Any

from db.client import DatabaseClient


class VisitRepository:
    def __init__(self, client: DatabaseClient) -> None:
        self._client = client

    def get_by_id(self, visit_id: int) -> dict[str, Any] | None:
        return self._client.fetch_one("SELECT * FROM visits WHERE id = %s", (visit_id,))

    def get_by_pet_id(self, pet_id: int) -> list[dict[str, Any]]:
        return self._client.fetch_all(
            "SELECT * FROM visits WHERE pet_id = %s ORDER BY id",
            (pet_id,),
        )

    def exists(self, visit_id: int) -> bool:
        return self.get_by_id(visit_id) is not None

    def delete_by_id(self, visit_id: int) -> int:
        return self._client.execute("DELETE FROM visits WHERE id = %s", (visit_id,))
