from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, func
from src.base import Base


class MetalRollORM(Base):  # Основная таблица
    __tablename__ = 'stock'

    id: Mapped[int] = mapped_column(primary_key=True)
    length: Mapped[int]
    weight: Mapped[int]
    data_add: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    data_del: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), )

class StatisticsDay(Base):  # Таблица со статистикой по дням
    __tablename__ = 'statistics_day'

    id: Mapped[int] = mapped_column(primary_key=True)
    day: Mapped[datetime] = mapped_column(DateTime(timezone=True), )
    countMetalRoll: Mapped[int]
    sumWeightMetalRoll: Mapped[int]