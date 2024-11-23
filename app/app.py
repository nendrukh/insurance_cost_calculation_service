from datetime import datetime

from database import TariffRepository, ResponseInsuranceCostRepository
from models import TariffSchema, TariffDbSchema, InsuranceCostSchema


class InsuranceWorker:
    @classmethod
    async def adding_tariff(cls, tariff_data: dict):
        for tariff_date, tariff_types in tariff_data.items():
            for tariff_type in tariff_types:
                tariff = TariffSchema.model_validate(
                    {
                        "date": tariff_date,
                        **tariff_type
                    }
                )
                await TariffRepository.add_tariff(tariff)

    @classmethod
    async def delete_tariff(cls, cargo_type: str, date: datetime) -> bool:
        return await TariffRepository.delete_tariff(cargo_type, date)

    @classmethod
    async def update_tariff(cls, cargo_type: str, date: datetime, new_rate: float) -> bool:
        return await TariffRepository.update_tariff(cargo_type, date, new_rate)

    @classmethod
    async def calculate_insurance(cls, cargo_type: str, date: datetime, cost: float) -> float | None:
        tariff: TariffDbSchema = await TariffRepository.get_tariff(cargo_type, date)
        if tariff is None:
            return

        insurance_cost = cost * float(tariff.rate)
        await ResponseInsuranceCostRepository.add_insurance_cost(
            InsuranceCostSchema.model_validate(
                {"tariff_id": tariff.id, "declared_price": cost, "insurance_cost": insurance_cost}
            )
        )

        return insurance_cost
