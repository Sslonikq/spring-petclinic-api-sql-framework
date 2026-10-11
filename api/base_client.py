from typing import Any

import allure
import requests
from requests import Response

from config.settings import settings


class BaseApiClient:
    def __init__(self, base_url: str | None = None, timeout: int = 10) -> None:
        self.base_url = (base_url or settings.api_base_url).rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.trust_env = False
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    def _build_url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    @staticmethod
    def _attach(response: Response) -> None:
        request_body = response.request.body
        if isinstance(request_body, bytes):
            request_body = request_body.decode("utf-8")

        allure.attach(
            request_body or "",
            name="Request",
            attachment_type=(
                allure.attachment_type.JSON if request_body else allure.attachment_type.TEXT
            ),
        )
        allure.attach(
            f"{response.status_code}\n{response.text}",
            name="Response",
            attachment_type=allure.attachment_type.TEXT,
        )

    def _request(self, method: str, path: str, **kwargs: Any) -> Response:
        url = self._build_url(path)
        with allure.step(f"{method} {path}"):
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            self._attach(response)
        return response

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
