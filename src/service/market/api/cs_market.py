import aiohttp
import time, asyncio
from typing import Any


class CSMarket:
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._min_delay = 0.2
        self._last_request_time: float = 0
        self._lock = asyncio.Lock()

    async def _limit_rate(self):
        """
            Summary: Ограничивает частоту запросов до

            Parameters:

            Return: None
        """
        async with self._lock:
            elapsed = time.time() - self._last_request_time
            if elapsed < self._min_delay:
                await asyncio.sleep(self._min_delay - elapsed)
            self._last_request_time = time.time()

    async def _make_request(self, url: str, method: str):

        await self._limit_rate()

        async with aiohttp.ClientSession() as session:
            async with session.request(url=url, method=method) as response:
                response_status = response.status

                if response_status == 200:
                    res = await response.json()
                    return response_status, res

                return response_status, {
                    'status': False,
                    'message': 'Сервер не ответил на соединение'
                }

    async def get_inventory_steam(self, lang: str = 'ru') -> tuple[bool, dict[str, Any]]:
        """
            Summary: Получить весь инвентарь Steam аккаунта
                    * Получаем только те предметы, которые можно выставить на продажу

            Parameters:
                * lang: str - язык. По умолчанию значение ru

            Return:
                Dict[str, Any]

                {
                    "success": true,
                    "items": [
                        {
                            "id": "14933635912",
                            "classid": "310776767",
                            "instanceid": "0",
                            "market_hash_name": "SCAR-20 | Carbon Fiber (Factory New)",
                            "market_price": 10.34,
                            "tradable": 1
                        }
                    ]
                }
        """

        status, response = await self._make_request(
            url=f'https://market.csgo.com/api/v2/my-inventory?key={self._api_key}&lang={lang}',
            method='post'
        )

        if status == 200:
            return True, response

        return False, response

    async def get_items_for_sale(self) -> dict[str, Any]:
        """
            Summary: Получить список предметов, выстравленных на продажу

            Parameters:

            Return:
                Dict[str, Any]

                {
                    "success": true,
                    "items": [
                        {
                            "item_id": "286316844",
                            "assetid": "15092687536",
                            "classid": "637317999",
                            "instanceid": "630912635",
                            "real_instance": "1629337655",
                            "market_hash_name": "Horns of Monstrous Reprisal",
                            "position": 0,
                            "price": 4,
                            "currency": "RUB",
                            "status": "1",
                            "live_time": 920,
                            "left": null,
                            "botid": "0",
                            "settlement": 0,
                        }
                    ]
                }
        """

        status, response = await self._make_request(
            url=f'https://market.csgo.com/api/v2/items?key={self._api_key}',
            method='post'
        )

        if status == 200:
            return response

        return response

    async def put_item_up_sale(self, item_id: int, price_item: int | float, currency: str = 'RUB') -> dict[str, str]:
        """
            Summary: Выставить предмет на продажу

            Parameters:
                item_id: int - ID предмета из Steam
                price_item: int | float - цена прдемета
                * currency: str - валюта. По умолчанию значение RUB

            Return:
                Dict[str, stt | bool]

                {
                    'status': bool,
                    'message': str
                }
        """

        status, response = await self._make_request(
            url=f'https://market.csgo.com/api/v2/add-to-sale?key={self._api_key}&id={item_id}&price={price_item}&cur={currency}',
            method='post'
        )

        if status == 200:

            if response['success']:
                return {
                    'status': True,
                    'message': f'Предмет выставлен на продажу'
                }

            return {
                'status': False,
                'message': response['error']
            }

        return response

    async def update_price_item(self, item_id: int | str, new_price_item: int | float, currency: str = 'RUB') -> dict[
        str, str]:
        """
            Summary: Установить новую цена на предмет

            Parameters:

                item_id: int - ID предмета
                new_price_item: int | float - новая цена на предмет
                *currency: str - валюта. значение по умолчанию RUB

            Return:
                Dict[str, str | bool]

                {
                    'status': bool,
                    'message': str
                }
        """

        status, response = await self._make_request(
            url=f'https://market.csgo.com/api/v2/set-price?key={self._api_key}&item_id={item_id}&price={int(new_price_item)}&cur={currency}',
            method='post'
        )

        if status == 200:

            if response['success']:
                return {
                    'status': True,
                    'message': 'Цена изменена'
                }

            return {
                'status': False,
                'message': str(response['error']) + str(new_price_item)
            }

        return response

    async def list_best_prices(self) -> dict[str, Any]:
        """
            Summary: Получить список лучший цен

            Parameters:

            Return:
                Dict[str, Any]

                {
                    "success": true,
                    "time": 1765120214,
                    "currency": "RUB",
                    "items": [
                        {
                            "market_hash_name": "'Blueberries' Buckshot | NSWC SEAL",
                            "volume": "54",
                            "price": "1436.87"
                        },
                        {
                            "market_hash_name": "'Medium Rare' Crasswater | Guerrilla Warfare",
                            "volume": "52",
                            "price": "3212.67"
                        },
                    ...
                }
        """

        status, response = await self._make_request(
            url='https://market.csgo.com/api/v2/prices/RUB.json',
            method='get'
        )

        if status == 200:
            return response

        return response

    async def get_sales_history(self, date: str) -> dict[str, Any]:
        """
            Summary: Получение историю продаж предметов

            Parameters:
                date: str DD-MM-YYYY

            Return:
                dict[str, Any]

            TRADE_STAGE_NEW = 1 - Новый этап торговли
            TRADE_STAGE_ITEM_GIVEN = 2 - Получен товар для этапа торговли
            TRADE_STAGE_TIMED_OUT = 5 - Срок действия этапа торговли истек

            event: str
                |-- buy - предмет был куплен
                |-- sell - предмет был продан
        """

        status, response = await self._make_request(
            url = f'https://market.csgo.com/api/v2/history?key={self._api_key}&date={date}',
            method = 'post'
        )

        if status == 200:
            return response

        return response