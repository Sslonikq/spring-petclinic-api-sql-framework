from typing import Any

import requests
from requests import Response

from config.settings import settings


class BaseApiClient:
    def __init__(self, base_url: str | None = None, timeout: int = 10) -> None:
        self.base_url = (base_url or settings.api_base_url).rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    def _build_url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def _request(self, method: str, path: str, **kwargs: Any) -> Response:
        return self.session.request(method, self._build_url(path), timeout=self.timeout, **kwargs)

    def get(self, path: str, params: dict[str, Any] | None = None) -> Response:
        return self._request("GET", path, params=params)

    def post(self, path: str, data: dict[str, Any] | None = None) -> Response:
        return self._request("POST", path, json=data)

    def put(self, path: str, data: dict[str, Any] | None = None) -> Response:
        return self._request("PUT", path, json=data)

    def delete(self, path: str) -> Response:
        return self._request("DELETE", path)

    def close(self) -> None:
        self.session.close()
