from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import asyncio

from src.service.market.api.cs_market import CSMarket
from src.scripts.check_data import check_money, get_timestamps_in_seconds
from src.db.CRUD import user_database

stat = APIRouter(prefix="/stat", tags=["stat"])

@stat.get("/info")
async def get_stat_info(user_id):
    return FileResponse("src/web/statistic.html")

@stat.get("/api")
async def get_stat_api(user_id):
    user = user_database.get_info_by_id(int(user_id))

    market = CSMarket(user["api_key"])
    time = get_timestamps_in_seconds()

    data_today = await market.get_sales_history(time["today_start"])
    data_yesterday = await market.get_sales_history(time["yesterday_start"])
    data_week = await market.get_sales_history(time["week_monday_start"], time["week_sunday_end"])
    data_month = await market.get_sales_history(time["month_start"], time["month_end"])

    data_out_today = 0
    data_out_yesterday = 0
    data_out_week = 0
    data_out_month = 0

    if data_today["success"]:
        data_out_today = check_money(data_today)
    if data_yesterday["success"]:
        data_out_yesterday = check_money(data_yesterday)
    if data_week["success"]:
        data_out_week = check_money(data_week)
    if data_month["success"]:
        data_out_month = check_money(data_month)

    return {
        "today": data_out_today,
        "yesterday": data_out_yesterday,
        "month": data_out_month,
        "week": data_out_week,
    }