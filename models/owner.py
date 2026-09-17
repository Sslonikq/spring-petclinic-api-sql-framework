from typing import Any

from pydantic import Field

from models.base import PetClinicModel


class OwnerRequest(PetClinicModel):
    first_name: str = Field(max_length=30)
    last_name: str = Field(max_length=30)
    address: str = Field(max_length=255)
    city: str = Field(max_length=80)
    telephone: str = Field(max_length=20)


class OwnerResponse(OwnerRequest):
    id: int
    pets: list[dict[str, Any]] = Field(default_factory=list)
