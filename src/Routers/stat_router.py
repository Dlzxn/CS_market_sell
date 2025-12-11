from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import asyncio
from datetime import datetime, timedelta, timezone

from src.service.logger_cfg.log import logger
from src.service.market.api.cs_market import CSMarket
from src.scripts.check_data import check_money, get_timestamps_in_seconds
from src.db.CRUD import user_database

stat = APIRouter(prefix="/stat", tags=["stat"])

@stat.get("/info")
async def get_stat_info(user_id):
    return FileResponse("src/web/statistic.html")



def _get_start_of_day_timestamp(days_ago: int = 0) -> int:
    now = datetime.now(timezone.utc)
    target_date = now.date() - timedelta(days=days_ago)
    start_of_day = datetime.combine(target_date, datetime.min.time(), tzinfo=timezone.utc)
    return int(start_of_day.timestamp())


@stat.get("/api")
async def get_stat_api(user_id):
    user = user_database.get_info_by_id(int(user_id))

    if not user:
        return {"error": "User not found"}

    market = CSMarket(user["api_key"])

    days_to_fetch = 30
    fetch_start_ts = _get_start_of_day_timestamp(days_to_fetch)

    sales_history_response = await market.get_sales_history(fetch_start_ts)

    if not sales_history_response["success"]:
        return {"error": "Failed to fetch sales history"}

    all_sales = sales_history_response.get("items", [])

    today_start_ts = _get_start_of_day_timestamp(0)
    yesterday_start_ts = _get_start_of_day_timestamp(1)

    now = datetime.now(timezone.utc)
    week_start_date = now.date() - timedelta(days=now.weekday())
    week_start_ts = int(datetime.combine(week_start_date, datetime.min.time(), tzinfo=timezone.utc).timestamp())

    sales_today = []
    sales_yesterday = []
    sales_week = []

    for item in all_sales:
        item_time = item.get("time")
        if item_time is None or not isinstance(item_time, (int, float)):
            continue

        if item_time >= today_start_ts:
            sales_today.append(item)

        if item_time >= yesterday_start_ts and item_time < today_start_ts:
            sales_yesterday.append(item)

        if item_time >= week_start_ts:
            sales_week.append(item)

    data_out_today = check_money({"success": True, "items": sales_today})
    data_out_yesterday = check_money({"success": True, "items": sales_yesterday})
    data_out_week = check_money({"success": True, "items": sales_week})
    data_out_month = check_money(sales_history_response)

    return {
        "today": data_out_today,
        "yesterday": data_out_yesterday,
        "week": data_out_week,
        "month": data_out_month,
    }