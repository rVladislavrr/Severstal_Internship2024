from datetime import datetime, timezone, timedelta
from src.roll_warehouse.models import MetalRollORM, StatisticsDay
from src.roll_warehouse.shemas import MetalRoll, FilterAll
from sqlalchemy import select, and_, or_, func
from fastapi import HTTPException, status
from src.roll_warehouse.utils import help_selects, creat_Dict_day, sec_time_str, get_listFilter
from src.base import get_session


class MetalRollManager:  # Менеджер работы с бд

    @staticmethod
    async def create_stats():  # статика за прошедший день
        async with await get_session() as session:
            utc_time = datetime.now(timezone.utc).replace(microsecond=0, second=0, minute=0, hour=0)  # берём
            # сегодняшний день только в 00 и смотрим, которые были удалены сегодня или не удалены вообще,
            # те и есть на нашем складе
            filters = [MetalRollORM.data_del > utc_time, MetalRollORM.data_del == None]
            query = select(MetalRollORM).where(or_(*filters))
            res = (await session.execute(query)).scalars().all()
            count_rolls = len(res)
            sum_we_rolls = sum(map(lambda x: x.weight, res))
            day = StatisticsDay(day=utc_time,
                                countMetalRoll=count_rolls,
                                sumWeightMetalRoll=sum_we_rolls)
            session.add(day)
            await session.commit()

    @staticmethod
    async def add_t(roll, session):
        """
        Добавление объекта у которого есть вес и длинна в базу данных
        :param session: сессия
        :param roll: объект с весом и длинной
        :return: его же из бд с полученным индексом и временем создания
        """
        roll_in_orm = MetalRollORM(**roll.dict())
        session.add(roll_in_orm)
        await session.flush()

        roll = MetalRoll.model_validate(roll_in_orm, from_attributes=True)
        await session.commit()

        return roll

    @staticmethod
    async def delete(roll_id: int, session):
        """
        Удаление объекта из бд
        :param session: сессия
        :param roll_id: Индекс объекта которого хотим удалить
        :return: его же, но с временем удаления (либо 404)
        """
        query = select(MetalRollORM).filter_by(id=roll_id, data_del=None)
        stmt = await session.execute(query)
        roll_in_orm = stmt.scalars().one_or_none()
        if roll_in_orm:
            time = datetime.now(timezone.utc)
            roll_in_orm.data_del = time
            await session.flush()
            roll = MetalRoll.model_validate(roll_in_orm, from_attributes=True)
            await session.commit()

            return roll
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    @staticmethod
    async def filter_roll(f: FilterAll, session):
        """
        Фильтруем наши рулоны по заданным параметрам
        :param session: сессия
        :param f: объект с упорядочены ми фильтрами
        :return: лист рулонов подходящих по фильтрам
        """
        list_filters = get_listFilter(f)
        stmt = select(MetalRollORM).where(and_(*list_filters))
        result = (await session.execute(stmt)).scalars().all()
        return [MetalRoll.model_validate(r, from_attributes=True) for r in result]

    @staticmethod
    async def statistics(start, end, session):
        """
        Вся статистика вместе со статистикой по дням
        :param session: сессия
        :param start: стартовое время промежутка
        :param end: конец промежутка
        :return: Всю статистику в виде объекта
        """
        filAdd_ls_start = MetalRollORM.data_add < start
        filDel_or_ge_start_None = or_(
            MetalRollORM.data_del == None,
            MetalRollORM.data_del >= start,
        )
        fil_between_start_end = MetalRollORM.data_add.between(start, end)

        fil_Diapozon = and_(filAdd_ls_start, filDel_or_ge_start_None)
        fil_Diapozon = or_(fil_Diapozon, fil_between_start_end)

        query1 = select(MetalRollORM).filter(fil_between_start_end).order_by(MetalRollORM.data_add)
        roll_add_diapz = (await session.execute(query1)).scalars().all()

        query2 = select(MetalRollORM).filter(MetalRollORM.data_del.between(start, end)).order_by(
            MetalRollORM.data_add)
        roll_del_diapz = (await session.execute(query2)).scalars().all()

        query = select(MetalRollORM).filter(fil_Diapozon).order_by(MetalRollORM.data_add)
        roll_diapz = (await session.execute(query)).scalars().all()

        stats = await MetalRollManager.day_stats(start, end, session)

        sum_we = sum(map(lambda x: x.weight, roll_diapz))
        avg_we = sum_we / len(roll_diapz)
        avg_le = sum(map(lambda x: x.length, roll_diapz)) / len(roll_diapz)

        max_we = max_le = -1
        min_we = min_le = 10 ** 5
        max_time = timedelta(0)
        min_time = timedelta(days=365)
        for roll in roll_diapz:

            if max_we < roll.weight:
                max_we = roll.weight
            if min_we > roll.weight:
                min_we = roll.weight
            if max_le < roll.length:
                max_le = roll.length
            if min_le > roll.length:
                min_le = roll.length
            if roll.data_del is not None:
                if max_time < roll.data_del - roll.data_add:
                    max_time = roll.data_del - roll.data_add
                if min_time > roll.data_del - roll.data_add:
                    min_time = roll.data_del - roll.data_add

        if max_time == timedelta(0) and min_time == timedelta(days=365):
            max_time_str = min_time_str = "Не было удалённых рулонов за данный промежуток"
        else:
            max_time_str = sec_time_str(max_time)
            min_time_str = sec_time_str(min_time)
        return {
            "количество добавленных рулонов": len(roll_add_diapz),
            "количество удалённых рулонов": len(roll_del_diapz),
            "средняя длина, вес рулонов, находившихся на складе в этот период": {
                "Длинна": round(avg_le, 2),
                "Вес": round(avg_we, 2),
            },
            "максимальная и минимальная длина и вес рулонов, находившихся на складе в этот период": {
                "Максимум": {
                    "Длинна": max_le,
                    "Вес": max_we
                },
                "Минимум": {
                    "Длинна": min_le,
                    "Вес": min_we
                }
            },
            "суммарный вес рулонов на складе за период": sum_we,
            "максимальный и минимальный промежуток между добавлением и удалением рулона":
                {
                    "Максимальный": max_time_str,
                    "Минимальный": min_time_str
                }
        } | stats

    @staticmethod
    async def day_stats(start, end, session):
        """
        Отдоенная статистика по дням (если понадобиться отдельным вызовом)
        :param session: сессия
        :param start: время старт
        :param end: время конец
        :return: объект
        """
        answer = {}

        for i in [StatisticsDay.countMetalRoll, StatisticsDay.sumWeightMetalRoll]:
            query = help_selects(start, end, func.min(i), i)
            min_ = (await session.execute(query)).all()
            query = help_selects(start, end, func.max(i), i)
            max_ = (await session.execute(query)).all()
            if i == StatisticsDay.countMetalRoll:
                answer['Количество'] = {
                    'Максимальное': creat_Dict_day(max_),
                    'Минимальное': creat_Dict_day(min_),
                }
            else:
                answer['Вес'] = {
                    'Максимальный': creat_Dict_day(max_),
                    'Минимальный': creat_Dict_day(min_),
                }
        return {'Статистика по дням': answer}
