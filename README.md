# Severstal_Internship2024

## Фреймворк FastApi язык Python

В проекте так же были миграции.
Был бы рад получить обратную связь по поводу реализации проекта, тк интересно что можно было бы изменить и подправить и (или) убрать

## Статистика по дням
Статистика по дням реализованна, но она берет данные из таблицы (таблица со статистикой за день) и работает с ними, в таблицу данные добавляются автоматически каждый день.
Можно было бы настроить тригер на основную таблицу, что бы когда данные обновлялись статистика по дням так же обновлялась, но я не сделал этого.

### Реализовано:
- [x] добавление нового рулона на склад. Длина и вес — обязательные параметры. В случае успеха возвращает добавленный рулон;
- [x] удаление рулона с указанным id со склада. В случае успеха возвращает удалённый рулон;
- [x] получение списка рулонов со склада. Рассмотреть возможность фильтрации по одному из диапазонов единовременно (id/веса/длины/даты добавления/даты удаления со склада);
- [x] получение статистики по рулонам за определённый период:
### На дополнительные баллы 
- [x] Получение списка рулонов с фильтрацией (п.1, с.) работает по комбинации нескольких диапазонов сразу.
- [x] Получение статистики по рулонам за дни
- [x] Добавлены тесты (не покрывает всё, но они есть)
- [x] Конфигурации к подключению к БД должны быть настраиваемыми через файл или ENV.
#### Не уверен, но возможно:
- Проект должен быть обёрнут в Docker
- Проект должен проходить mypy, flake8 и прочее.
- Отсутствие глобальных переменных.
- Использование абстракций/интерфейсов для возможной замены транспорта. Например, 
с PostgreSQL на какое-нибудь хранилище (InMemory / Redis / File).
