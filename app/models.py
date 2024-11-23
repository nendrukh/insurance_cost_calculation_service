from datetime import datetime
from pydantic import BaseModel, field_validator


class TariffSchema(BaseModel):
    date: datetime
    cargo_type: str
    rate: float

    @field_validator("rate")
    @classmethod
    def field_validation(cls, field):
        return float(field)


class TariffDbSchema(TariffSchema):
    id: int


class InsuranceCostSchema(BaseModel):
    tariff_id: int
    declared_price: float
    insurance_cost: float
