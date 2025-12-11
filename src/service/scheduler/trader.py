import asyncio, time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import JobLookupError

from src.service.logger_cfg.log import logger
from src.service.market.api.cs_market import CSMarket
from src.db.CRUD import user_database
from src.service.market.checking_item_price import checking_item_price
from src.model.DataModel import DataModel, UpdateTimeData, SkinSettings


async def delete_skins(user_id):
    user = user_database.get_info_by_id(user_id)

    if not user:
        logger.warning(f"delete_skins: Пользователь с ID {user_id} не найден в БД.")
        return

    logger.info(f"Начало проверки и удаления проданных скинов для ID: {user_id}")

    market = CSMarket(user["api_key"])
    list_skins_response = await market.get_items_for_sale()

    if not list_skins_response.get("success"):
        logger.error(
            f"Ошибка получения списка предметов для продажи у id {user_id}: {list_skins_response.get('error', 'Нет информации об ошибке')}")
        return

    active_api_ids = {str(skin["item_id"]) for skin in list_skins_response.get("items", [])}

    skins_to_check = user.get("skins", [])

    for skin in skins_to_check:
        db_item_id = str(skin.get("id"))

        if db_item_id not in active_api_ids:

            item_name = skin.get("market_hash_name", f"ID:{db_item_id}")

            stat = user_database.delete_skin(user_id, int(db_item_id))

            if stat:
                logger.info(f"Скин {item_name} (ID: {db_item_id}) удален из БД у id {user_id} (Продан/Снят).")
            else:
                logger.error(f"Ошибка удаления скина {item_name} из БД у id {user_id}.")

    cached_items = user_database.get_all_cached_items()

    for cached_item in cached_items:
        cached_item_id = str(cached_item["item_id"])

        if cached_item_id not in active_api_ids:

            stat = user_database.delete_cached_item(cached_item_id)

            if stat:
                logger.info(f"Кэш: Запись о предмете {cached_item_id} удалена из кэша цен (Продан/Снят).")

    return







async def check_new_skins(user_id: int | str):
    logger.info("ЗАПУЩЕН ПРОСМОТР ДЛЯ АЙДИ: " + str(user_id))
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
    logger.info("Сервер ответил на соединение-инвентарь получен")
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
    user = user_database.get_info_by_id(user_id)
    if user is None:
        logger.info(f"Пользователь с id {user_id} не найден")
        return 0
    else:
        market = CSMarket(user["api_key"])
        list_items = await market.get_items_for_sale()
        info = await market.list_best_prices()
        best_prices_map = {
            skin["market_hash_name"]: int(float(skin["price"]) * 100)
            for skin in info["items"]
        }
        try:
            if not list_items["success"]:
                logger.error(f"Ответ от сервера не получен | запрос всех item на продажу для айди {user_id}")
                return 0
        except KeyError as e:
            logger.error(f"Не найден ключ success, данные выглядят так: {list_items}")

        try:
            if list_items["items"]:
                pass
        except KeyError as e:
            return 0

        for item in list_items["items"]:
            is_find = False
            for x in user["skins"]:
                if str(x["id"]) == str(item["item_id"]):
                    is_find = True
                    bd_skin = x
                    break

            if is_find:
                if not bd_skin["auto_reprice"]:
                    logger.info(f"Данный скин не торгуется")
                    continue

            skin_hash = item["market_hash_name"]
            if int(item["position"]) == 1:
                logger.info(f"Позиция предмета {skin_hash} занимает 1 место")
                continue

            flag = False
            try:
                price_best = best_prices_map[skin_hash]
                price = price_best
                flag = True

            except KeyError:
                logger.error(f"Ошибка нахождения скина {skin_hash} в лучших ценах")

            except Exception as e:
                logger.error(e)

            if not flag:
                logger.info("Скин не найден среди всех items")
                continue

            print(f"Цены на скин {skin_hash}: {price} | {int(float(item["price"])*100)}")
            if price == item["price"]:
                logger.info(f"Скин {skin_hash} стоит по актуальному прайсу")
                continue

            status = user_database.checking_item_price(user_id, item["item_id"], price)
            match status:
                case 0:
                    logger.info(f"Защита от демпинга для скина {skin_hash}, актуальная цена станет {price + 1}")
                    price += 2
                case 1:
                    pass

            status = await market.update_price_item_mhn(market_hash_name=skin_hash, new_price_item=price-1)
            try:
                if status["success"]:
                    logger.info(f"Цена на предмет {skin_hash} изменена на {price-1}")
                else:
                    logger.error(f"Ошибка изменения цены для скина"
                                 f" с id {item["item_id"]} по прайсу {price-1}")
            except Exception as e:
                logger.error(f"Ошибка изменения цены: {status["message"]} для скина"
                                 f" с id {item["item_id"]} по прайсу {price-1}")
        return None