from datetime import datetime, timezone
from fastapi import APIRouter, status, Depends
from asyncpg import ConnectionDoesNotExistError
from sqlalchemy.ext.asyncio import AsyncSession

from src.base import get_async_session,get_session
from src.roll_warehouse.shemas import MetalRollAdd, MetalRoll, FilterAll
from src.roll_warehouse.manager import MetalRollManager
from fastapi import HTTPException, Query

router = APIRouter(
    tags=['Склад рулонов металла']
)


@router.get('/filters', response_model=list[MetalRoll], name='Получение рулонов по фильтрам', )
async def get_rolls_by_filters(
        id_start: int = Query(default=None, gt=0, ),
        id_end: int = Query(default=None, gt=0,),
        length_start: int = Query(default=None, gt=0,),
        length_end: int = Query(default=None, gt=0),
        weight_start: int = Query(default=None, gt=0),
        weight_end: int = Query(default=None, gt=0),
        data_add_start: datetime = Query(default=None),
        data_add_end: datetime = Query(default=None),
        data_del_start: datetime = Query(default=None),
        data_del_end: datetime = Query(default=None),
        session: AsyncSession = Depends(get_async_session),
):  # расписал каждую для удобства работы в документации FastApi, а так же для более точной фильтрации
    # (работает по нескольким вместе)
    try:

        f = FilterAll(**{
            "id": {"start": id_start, "end": id_end} if id_start or id_end else None,
            "length": {"start": length_start, "end": length_end} if length_start or length_end else None,
            "weight": {"start": weight_start, "end": weight_end} if weight_start or weight_end else None,
            "data_add": {"start": data_add_start, "end": data_add_end} if data_add_start or data_add_end else None,
            "data_del": {"start": data_del_start, "end": data_del_end} if data_del_start or data_del_end else None,
        })
        rolls = await MetalRollManager.filter_roll(f, session)
        return rolls
    except ConnectionDoesNotExistError as e:  # ошибка подключения к бд
        print(e)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    except Exception as e:  # все остальные ошибки
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post('/add', status_code=status.HTTP_201_CREATED, name='Добавление рулона')
async def add_datab(
        roll: MetalRollAdd,
        session: AsyncSession = Depends(get_async_session),
) -> MetalRoll:  # добавление рулона в бд по весу и длине, время ставиться автоматом как и индекс
    try:
        roll_orm = await MetalRollManager.add_t(roll, session)
        return roll_orm
    except ConnectionDoesNotExistError as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.delete('/del/{id_roll}', name='Удаление рулона', )
async def delete(
        id_roll: int,
        session: AsyncSession = Depends(get_async_session),
) -> MetalRoll:  # удаление рулона время ставиться автоматом
    try:
        roll_orm = await MetalRollManager.delete(id_roll, session)
        return roll_orm
    except HTTPException:  # вылетает 404 если не нашлось
        raise
    except ConnectionDoesNotExistError as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/statistics", name='получение всей статистики')
async def get_statistics(
        date_start: datetime = Query(default=datetime.min, alias='Время с какого считать в UTC'),
        date_end: datetime = Query(default=datetime.now(), alias='Время конечное в UTC'),
        session: AsyncSession = Depends(get_async_session),
):  # получаю всю статистику нужную по заданию
    try:
        date_start = date_start.replace(tzinfo=timezone.utc)
        date_end = date_end.replace(tzinfo=timezone.utc)
        if date_start > date_end:
            raise HTTPException(status_code=400, detail='start must be less than end')

        statistics = await MetalRollManager.statistics(date_start, date_end, session)
        return statistics
    except ConnectionDoesNotExistError as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


async def collect_statistics(): # функция на добавление данных статистики в бд за прошедший день
    try:
        await MetalRollManager.create_stats()
    except ConnectionDoesNotExistError as e:
        print(e)
