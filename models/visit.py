import datetime

from pydantic import Field

from models.base import PetClinicModel


class VisitRequest(PetClinicModel):
    date: datetime.date | None = None
    description: str = Field(max_length=255)


class VisitResponse(VisitRequest):
    id: int
    pet_id: int
