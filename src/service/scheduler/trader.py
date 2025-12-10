import asyncio, time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import JobLookupError

from src.service.logger_cfg.log import logger
from src.service.market.api.cs_market import CSMarket
from src.db.CRUD import user_database
from src.service.market.checking_item_price import checking_item_price
from src.model.DataModel import DataModel, UpdateTimeData, SkinSettings


async def delete_skins(user_id):
    if user_id == 0:
        return 0
    user = user_database.get_info_by_id(user_id)
    print(user)
    print("Получены данные с бд о пользователи с айди:", user_id)

    market = CSMarket(user["api_key"])
    list_skins = await market.get_items_for_sale()
    index_list = []
    for x in user["skins"]:
        flag = False
        for skin in list_skins["items"]:
            if str(skin["item_id"]) == str(x["id"]):
                flag = True
                index_list.append(x["id"])
                break
        if not flag:
            stat = user_database.delete_skin(user_id, x["id"])

    for x in list_skins["items"]:
        if x["item_id"] not in index_list:
            skin = SkinSettings(user_id=user_id, skin_id=x["item_id"], enabled=True, min=0)
            stat = user_database.update_skin(skin)
            if stat:
                logger.info(f"Скин {x["market_hash_name"]} добавлен в бд")
            else:
                logger.error(f"При выставлении скина случилась ошибка | "
                             f"Ошибка базы данных")
    return 1


async def check_new_skins(user_id: int | str):
    print("ЗАПУЩЕН ПРОСМОТР ДЛЯ АЙДИ:", user_id)
    if user_id == 0:
        return 0
    user = user_database.get_info_by_id(user_id)
    market = CSMarket(user["api_key"])
    info = await market.list_best_prices()
    lots = info["items"]
    status, list_for_sale = await market.get_inventory_steam()
    if not status:
        logger.error(f"Ошибка получения инвентаря у id {user_id}")
        print(list_for_sale)
        return 0
    print("Сервер ответил на соединение-инвентарь получен")
    all_id = [x["id"] for x in user["skins"]]
    for x in list_for_sale["items"]:
        price = 0
        if x["id"] in all_id:
            continue
        else:
            for item in lots:
                if x["market_hash_name"] == item["market_hash_name"]:
                    price = item["price"]
                    status = await market.put_item_up_sale(x["id"], float(item["price"])*100 - 1)
                    if status["status"]:
                        skin = SkinSettings(user_id=user_id, skin_id=x["id"], enabled=True, min=0)
                        stat = user_database.update_skin(skin)
                        if stat:
                            logger.info(f"Скин f{x["market_hash_name"]} выставлен за {float(item["price"])*100 - 1} | id_user: f{user_id}")
                        else:
                            logger.error(f"При выставлении скина f{x["market_hash_name"]} случилась ошибка | "
                                         f"Ошибка базы данных  | id_user: f{user_id}")
                    else:
                        logger.error(f"При выставлении скина f{x["market_hash_name"]} случилась ошибка | "
                                     f"{status["message"]}  | id_user: f{user_id}")


async def check_user_orders(user_id: int | str) -> None:
    if user_id == 0:
        return 0
    time_start = time.time()
    user = user_database.get_info_by_id(user_id)
    if user is None:
        pass
    else:
        market = CSMarket(user["api_key"])
        list = await market.get_items_for_sale()
        try:
            stat = list["status"]
            logger.error(f"Ошибка обращения get_items_for_sale() у айди {user_id}, message: {list["message"]}")
            return 0
        except KeyError:
            pass

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
                        match status:
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
                                logger.error(f"Ошибка изменения цены: {status["message"]}")
                            break
                        else:
                            logger.info(f"Цена на предмет {hash_name} не изменена")
                            break

    print(f"Выполнено за : {time.time() - time_start}")
