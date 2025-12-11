from datetime import datetime, timedelta, date


def check_money(data):
    # Проверяем, что запрос успешен и что есть ключ "items"
    if not data.get("success") or not isinstance(data.get("items"), list):
        return 0.0

    return_sum = 0.0

    for item in data["items"]:
        price_cents = item.get("price")

        if price_cents is not None:
            return_sum += (price_cents / 100.0)

    return round(return_sum, 2)


def get_timestamps_in_seconds() -> dict:
    """
    Рассчитывает UNIX-метки времени (в секундах) для ключевых дат.
    """
    today_date = date.today()
    today_start = datetime(today_date.year, today_date.month, today_date.day)

    today_timestamp = int(today_start.timestamp())

    yesterday_start = today_start - timedelta(days=1)
    yesterday_timestamp = int(yesterday_start.timestamp())

    days_to_monday = today_start.weekday()
    monday_start = today_start - timedelta(days=days_to_monday)
    monday_timestamp = int(monday_start.timestamp())

    next_monday_start = monday_start + timedelta(weeks=1)
    sunday_end = next_monday_start - timedelta(seconds=1)

    sunday_timestamp = int(sunday_end.timestamp())

    first_of_month_start = datetime(today_date.year, today_date.month, 1)
    first_of_month_timestamp = int(first_of_month_start.timestamp())

    if today_date.month == 12:
        next_month_year = today_date.year + 1
        next_month = 1
    else:
        next_month_year = today_date.year
        next_month = today_date.month + 1

    first_of_next_month_start = datetime(next_month_year, next_month, 1)

    end_of_month = first_of_next_month_start - timedelta(seconds=1)
    end_of_month_timestamp = int(end_of_month.timestamp())

    return {
        "today_start": today_timestamp,
        "yesterday_start": yesterday_timestamp,
        "week_monday_start": monday_timestamp,
        "week_sunday_end": sunday_timestamp,
        "month_start": first_of_month_timestamp,
        "month_end": end_of_month_timestamp,
    }