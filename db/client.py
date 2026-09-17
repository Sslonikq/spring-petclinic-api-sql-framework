from typing import Any

import psycopg
from psycopg.rows import dict_row

from config.settings import settings


class DatabaseClient:
    def __init__(self, dsn: str | None = None) -> None:
        self._dsn = dsn or self._build_dsn()
        self._connection: psycopg.Connection | None = None

    @staticmethod
    def _build_dsn() -> str:
        return (
            f"host={settings.db_host} "
            f"port={settings.db_port} "
            f"dbname={settings.db_name} "
            f"user={settings.db_user} "
            f"password={settings.db_password.get_secret_value()}"
        )

    def _get_connection(self) -> psycopg.Connection:
        if self._connection is None or self._connection.closed:
            self._connection = psycopg.connect(
                self._dsn,
                row_factory=dict_row,
                autocommit=True,
            )
        return self._connection

    def _execute(self, query: str, params: tuple[Any, ...] | None = None) -> psycopg.Cursor:
        cursor = self._get_connection().cursor()
        cursor.execute(query, params)
        return cursor

    def fetch_one(self, query: str, params: tuple[Any, ...] | None = None) -> dict[str, Any] | None:
        with self._execute(query, params) as cursor:
            return cursor.fetchone()

    def fetch_all(self, query: str, params: tuple[Any, ...] | None = None) -> list[dict[str, Any]]:
        with self._execute(query, params) as cursor:
            return cursor.fetchall()

    def execute(self, query: str, params: tuple[Any, ...] | None = None) -> int:
        with self._execute(query, params) as cursor:
            return cursor.rowcount

    def close(self) -> None:
        if self._connection is not None and not self._connection.closed:
            self._connection.close()
        self._connection = None
