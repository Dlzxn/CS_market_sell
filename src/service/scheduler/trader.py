import asyncio, time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import JobLookupError

from src.service.logger_cfg.log import logger
from src.service.market.api.cs_market import CSMarket
from src.db.CRUD import user_database

async def check_user_orders(user_id: int | str) -> None:
    time_start = time.time()
    user = user_database.get_info_by_id(user_id)
    if user is None:
        pass
    else:
        market = CSMarket(user["api_key"])
        list = await market.get_items_for_sale()
        print(list["items"], len(list["items"]))

        for x in user["skins"]:
            print("Ищем скин в инвенторе...")
            for y in list["items"]:
                if str(y["item_id"]) == str(x["id"]):
                    print("Нашли")
                    if str(y["position"]) == "1":
                        print("Позиция итак первая")
                        break
                    else:
                        info = await market.get_inventory_steam()
                        lots = info["items"]
                        price = y["price"]
                        print(f"Длина лотов: {len(lots)}")
                        for lot in lots:
                            print(str(lot["classid"]), str(x["id"]))
                            if str(lot["id"]) == str(x["id"]) or str(lot["classid"]) == str(x["id"]):
                                print(f"Нашли цену в {lot["market_price"] - 0.01}")
                                price = lot["market_price"] - 0.01
                        print(f"Новая цена стала: {price}")
                        if price < x["min_price"]:
                            break
                        status = await market.update_price_item(item_id=x["id"], new_price_item=price)
                        if status:
                            logger.info(f"Цена на предмет с айди {x["id"]} изменена")
                        else:
                            logger.error(status["message"])
                        break
    print(f"Выполнено за : {time.time() - time_start}")
