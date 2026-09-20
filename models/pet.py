from datetime import date
from typing import Any

from pydantic import Field

from models.base import PetClinicModel


class PetType(PetClinicModel):
    id: int
    name: str


class PetRequest(PetClinicModel):
    name: str = Field(max_length=30)
    birth_date: date
    type: PetType


class PetResponse(PetRequest):
    id: int
    owner_id: int
    visits: list[dict[str, Any]] = Field(default_factory=list)
