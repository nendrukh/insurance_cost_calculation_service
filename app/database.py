from datetime import datetime

from config import POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT
from models import TariffSchema, TariffDbSchema, InsuranceCostSchema

from sqlalchemy import ForeignKey, select, delete, update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, Mapped, mapped_column


Base = declarative_base()


class Tariff(Base):
    __tablename__ = "tariffs"
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime]
    cargo_type: Mapped[str]
    rate: Mapped[float]


class InsuranceCost(Base):
    __tablename__ = "insurance_costs"
    id: Mapped[int] = mapped_column(primary_key=True)
    tariff_id: Mapped[int] = mapped_column(ForeignKey("tariffs.id", ondelete="CASCADE", onupdate="CASCADE"))
    declared_price: Mapped[float]
    insurance_cost: Mapped[float]


class Database:
    engine = create_async_engine(
        f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    session = async_sessionmaker(engine)

    @classmethod
    async def create_tables(cls):
        async with cls.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


class TariffRepository(Database):
    @classmethod
    async def add_tariff(cls, tariff: TariffSchema):
        data = tariff.model_dump()
        new_tariff = Tariff(**data)

        async with cls.session() as new_session:
            new_session.add(new_tariff)
            await new_session.flush()
            await new_session.commit()

    @classmethod
    async def get_tariff(cls, category: str, date: datetime) -> TariffDbSchema | None:
        query = select(Tariff).where(Tariff.cargo_type == category, Tariff.date == date)
        async with cls.session() as new_session:
            db_response = await new_session.execute(query)

        db_response = db_response.scalar()
        if db_response is None:
            return

        return TariffDbSchema.model_validate(
            {
                "id": db_response.id,
                "date": db_response.date,
                "cargo_type": db_response.cargo_type,
                "rate": db_response.rate
            }
        )

    @classmethod
    async def delete_tariff(cls, cargo_type: str, date: datetime) -> bool:
        async with cls.session() as new_session:
            query = delete(Tariff).where(Tariff.date == date, Tariff.cargo_type == cargo_type)
            db_response = await new_session.execute(query)

            if db_response.rowcount == 0:
                return False
            await new_session.commit()

        return True

    @classmethod
    async def update_tariff(cls, cargo_type: str, date: datetime, new_rate: float) -> bool:
        async with cls.session() as new_session:
            query = (
                update(Tariff)
                .where(Tariff.date == date, Tariff.cargo_type == cargo_type)
                .values(rate=new_rate)
            )
            db_response = await new_session.execute(query)

            if db_response.rowcount == 0:
                return False
            await new_session.commit()

        return True


class ResponseInsuranceCostRepository(Database):
    @classmethod
    async def add_insurance_cost(cls, insurance_schema: InsuranceCostSchema):
        data = insurance_schema.model_dump()
        new_insurance_cost = InsuranceCost(**data)

        async with cls.session() as new_session:
            new_session.add(new_insurance_cost)
            await new_session.flush()
            await new_session.commit()
