from src.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# соединение с бд
engine = create_async_engine(
        url=settings.DATABASE_URL,
        # echo=True, подсказки по обращению к бд
)

# создатель асинхронных сессий
async_session = async_sessionmaker(
    engine,
)
async def get_async_session():
    return async_session()


class Base(DeclarativeBase): # основа orm бд
    def __repr__(self) -> str:
        cols = [f"{col}={getattr(self, col)}" for col in self.__table__.columns.keys()]
        return f"<{self.__class__.__name__}: {', '.join(cols)}>"