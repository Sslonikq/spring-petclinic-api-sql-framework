from typing import Any

from faker import Faker

from models.pet import PetRequest, PetType

faker = Faker()

DEFAULT_PET_TYPE = PetType(id=2, name="dog")


class PetFactory:
    @staticmethod
    def build(**overrides: Any) -> PetRequest:
        data = {
            "name": faker.first_name(),
            "birth_date": faker.date_between(start_date="-10y", end_date="today"),
            "type": DEFAULT_PET_TYPE,
        }
        data.update(overrides)
        return PetRequest(**data)
