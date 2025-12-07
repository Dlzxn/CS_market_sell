import asyncio, time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import JobLookupError

from src.service.logger_cfg.log import logger
from src.service.market.api.cs_market import CSMarket
from src.db.CRUD import user_database
from src.service.market.checking_item_price import checking_item_price

async def check_user_orders(user_id: int | str) -> None:
    time_start = time.time()
    user = user_database.get_info_by_id(user_id)
    if user is None:
        pass
    else:
        market = CSMarket(user["api_key"])
        list = await market.get_items_for_sale()

        for x in user["skins"]:
            if not x["auto_reprice"]:
                logger.info("Данный скин не торгуется")
                continue
            for y in list["items"]:
                if str(y["item_id"]) == str(x["id"]):
                    hash_name = y["market_hash_name"]
                    if str(y["position"]) == "1":
                        logger.info("Позиция предмета занимает 1 место")
                        break
                    else:
                        info = await market.list_best_prices()
                        lots = info["items"]
                        price = y["price"]
                        flag = False
                        print(f"Длина лотов: {len(lots)}")
                        for lot in lots:
                            if str(lot["market_hash_name"]) == hash_name:
                                price = float(lot["price"])*100 - 1
                                logger.info(f"Нашли цену в {price}")
                                flag = True
                                break
                        status = checking_item_price(user_id, y["item_id"], price)
                        match(status):
                            case 0:
                                price += 2
                            case 1:
                                pass
                        flag_1 = False
                        if price < x["min_price"]:
                            price = x["min_price"]
                        print(f"Айди:{y["item_id"]}")
                        print(price, y["price"]*100)
                        if price != y["price"]*100:
                            status = await market.update_price_item(item_id=y["item_id"], new_price_item=price)
                            if status["status"]:
                                logger.info(f"Цена на предмет {hash_name} изменена на {price}")
                            else:
                                logger.error(status["message"])
                            break
                        else:
                            logger.info(f"Цена на предмет {hash_name} не изменена")
                            break

    print(f"Выполнено за : {time.time() - time_start}")
