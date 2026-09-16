from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_base_url: str

    db_engine: Literal["postgres", "mysql"] = "postgres"
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: SecretStr


settings = Settings()
