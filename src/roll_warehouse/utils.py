from datetime import timezone
from sqlalchemy import select
from src.roll_warehouse.models import StatisticsDay, MetalRollORM
from src.roll_warehouse.shemas import FilterAll


def help_selects(start, end, foo, obj):
    """
    Функция, которая делает select с подзапросом по дням
    :param start: стартовое время
    :param end: конечное время
    :param foo: функция (даётся либо минимальное или максимально значение)
    :param obj: объект по которому искать с помощью функции
    :return: объект запроса который мы можем отправить в бд
    """
    subq = select(foo
                  ).filter(StatisticsDay.day.between(start, end))

    query = select(StatisticsDay.day, obj
                   ).filter(obj == subq.as_scalar())
    return query


def creat_Dict_day(obj):
    if obj:
        return {'День': obj[0], "Ответ": obj[1]}
    else:
        return 'Нет статистики по дням (Таблица пуста)'

def sec_time_str(time):
    """
    Переводим из секунд в часы:минуты:секунды
    :param time: время в секундах
    :return: часы:минуты:секунды (str)
    """
    return str(int(time.total_seconds() // 3600)) + ":" + str(
        int((time.total_seconds() % 3600) // 60)).zfill(2) + ":" + str(
        int(time.total_seconds() % 60)).zfill(2)

def get_listFilter(f: FilterAll):
    """
    Создаём фильтры по полученым фильтрам
    :param f: объект с фильтрами
    :return: лист фильтров которые может добавить в select запрос
    """

    list_filters = []
    for field, _ in f.__fields__.items():
        att = getattr(f, field)
        if att and att.check():
            if att.start:
                if field in ["data_del", "data_add"]:
                    att.start = att.start.replace(tzinfo=timezone.utc)
                list_filters.append(getattr(MetalRollORM, field) >= att.start)
            if att.end:
                if field in ["data_del", "data_add"]:
                    att.end = att.end.replace(tzinfo=timezone.utc)
                list_filters.append(getattr(MetalRollORM, field) <= att.end)
    if getattr(f, "data_del"):
        return list_filters
    else:
        list_filters.append(MetalRollORM.data_del == None)
        return list_filters