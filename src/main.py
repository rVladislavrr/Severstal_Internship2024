from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.roll_warehouse.router import collect_statistics, router as router_roll

app = FastAPI()  # Создал переменную отвечающую за приложение
app.include_router(router_roll)  # подключил роутер отвечающий за логику
scheduler = AsyncIOScheduler()


@app.on_event("startup")  # при старте приложение создаётся штука которая будет создавать
# и заполнять таблицу со статистикой за этот день
async def startup():
    scheduler.add_job(collect_statistics, "cron", hour=23, minute=58, timezone="UTC")
    scheduler.start()


@app.on_event("shutdown")  # при закрытии она выключается
async def shutdown_event():
    scheduler.shutdown()
