from fastapi import FastAPI
from  fastapi.responses import FileResponse
import httpx, asyncio, sys
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import JobLookupError
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta

from src.model.DataModel import DataModel, UpdateTimeData
from src.Routers.user_rout import user_rout
from src.db.CRUD import user_database
from src.service.scheduler.trader import check_user_orders, delete_skins, check_new_skins
from src.service.logger_cfg.log import logger

scheduler = AsyncIOScheduler()


def startup_event(user_id):
    """Запускает планировщик при старте сервера."""
    user_id = int(user_id)
    if not scheduler.running:
        scheduler.start()
    scheduler.add_job(
            delete_skins,
            'interval',
            seconds=180,
            args=[user_id],
            id="delete_skins: "+ str(user_id),
            max_instances=1,
            next_run_time=datetime.now() + timedelta(seconds=1)
        )
    print("APScheduler запущен и готов к работе.")


async def main():
    """Асинхронная функция для запуска планировщика и ожидания."""
    user_id = sys.argv[1]
    startup_event(user_id)
    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Планировщик остановлен.")


if __name__ == '__main__':
    asyncio.run(main())
startup_event()

