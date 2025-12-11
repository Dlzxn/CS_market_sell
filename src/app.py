from fastapi import FastAPI
from  fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import JobLookupError
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta

from src.Routers import stat_router
from src.model.DataModel import DataModel, UpdateTimeData
from src.Routers.user_rout import user_rout
from src.db.CRUD import user_database
from src.service.scheduler.trader import check_user_orders, delete_skins, check_new_skins
from src.service.logger_cfg.log import logger
from src.Routers.stat_router import stat

app = FastAPI()
app.mount("/static", StaticFiles(directory="src/web"), name="static")
scheduler = AsyncIOScheduler()

def start_trader(user_id: int | str, interval: int | str):
    try:
        scheduler.remove_job(job_id=str(user_id))
        logger.info(f"Trader work{user_id} removed")
    except JobLookupError:
        pass
    scheduler.add_job(
        check_user_orders,
        'interval',
        seconds=interval,
        args=[user_id],
        id=str(user_id),
        max_instances=1
    )
    logger.info(f"Задача для User ID {user_id} обновлена. Интервал: {interval} с.")


@user_rout.post("/updates_time")
async def update_time(data: UpdateTimeData):
    status = user_database.update_time(data)
    start_trader(data.user_id, data.check_interval)
    return {"status": status}

@app.on_event("startup")
def startup_event():
    """Запускает планировщик при старте сервера."""
    if not scheduler.running:
        scheduler.start()
    all_id = user_database.get_all_id()
    print(all_id)
    for user_id, time in all_id:
        if str(user_id) == "0":
            continue
        print(user_id, time)
        scheduler.add_job(
            check_user_orders,
            'interval',
            seconds=time,
            args=[user_id],
            id=str(user_id),
            max_instances=1
        )
        scheduler.add_job(
            check_new_skins,
            'interval',
            seconds=600,
            args=[user_id],
            id="check_new_skins: " + str(user_id),
            max_instances=1,
            next_run_time=datetime.now() + timedelta(seconds=120)
        )
        scheduler.add_job(
            delete_skins,
            'interval',
            seconds=3600,
            args=[user_id],
            id="delete_skins: "+ str(user_id),
            max_instances=1,
            next_run_time=datetime.now() + timedelta(seconds=1800)
        )
    print("APScheduler запущен и готов к работе.")

@app.on_event("shutdown")
def shutdown_event():
    """Корректно останавливает планировщик при выключении сервера."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
    print("APScheduler остановлен.")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user_rout)
app.include_router(stat)

@app.get("/")
async def root():
    return {"message": "Hello"}

@app.get("/info")
async def info():
    return FileResponse("data/Info.pdf")