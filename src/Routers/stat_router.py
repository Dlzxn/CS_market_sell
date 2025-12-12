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

    # === timestamps ===
    now = datetime.now(timezone.utc)

    today_start_ts = _get_start_of_day_timestamp(0)
    yesterday_start_ts = _get_start_of_day_timestamp(1)

    last_7_days_ts = int((now - timedelta(days=7)).timestamp())
    last_30_days_ts = int((now - timedelta(days=30)).timestamp())

    sales_history_response = await market.get_sales_history(last_30_days_ts, now.timestamp())
    try:
        if not sales_history_response["success"]:
            return {"error": "Failed to fetch sales history"}
    except Exception as e:
        return {"error": "Failed to fetch sales history"}

    all_sales = sales_history_response.get("data", [])

    sales_today = []
    sales_yesterday = []
    sales_7d = []

    for item in all_sales:
        ts_str = item.get("time")
        if ts_str is None:
            continue

        try:
            ts = int(ts_str)
        except ValueError:
            logger.warning(f"Invalid timestamp: {ts_str}")
            continue

        # Today
        if ts >= today_start_ts:
            sales_today.append(item)

        # Yesterday
        if yesterday_start_ts <= ts < today_start_ts:
            sales_yesterday.append(item)

        # Last 7 days
        if ts >= last_7_days_ts:
            sales_7d.append(item)

    return {
        "today": check_money({"success": True, "data": sales_today}),
        "yesterday": check_money({"success": True, "data": sales_yesterday}),
        "week": check_money({"success": True, "data": sales_7d}),
        "month": check_money({"success": True, "data": all_sales}),
    }
