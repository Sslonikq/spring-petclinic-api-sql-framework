from typing import Any

from faker import Faker

from models.owner import OwnerRequest

faker = Faker()


class OwnerFactory:
    @staticmethod
    def build(**overrides: Any) -> OwnerRequest:
        data = {
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "address": faker.street_address(),
            "city": faker.city(),
            "telephone": faker.numerify("##########"),
        }
        data.update(overrides)
        return OwnerRequest(**data)

    @staticmethod
    def unique_last_name() -> str:
        return f"Qa{faker.pystr(min_chars=8, max_chars=8)}"
