from typing import Any

from faker import Faker

from models.visit import VisitRequest

faker = Faker()


class VisitFactory:
    @staticmethod
    def build(**overrides: Any) -> VisitRequest:
        data = {
            "date": faker.date_between(start_date="-1y", end_date="today"),
            "description": faker.sentence(nb_words=4),
        }
        data.update(overrides)
        return VisitRequest(**data)
