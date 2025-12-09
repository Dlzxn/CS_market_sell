import aiohttp
from typing import Any



class CSMarket:
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    async def _make_request(self, url: str, method: str):
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

    async def get_inventory_steam(self, lang: str = 'ru') -> dict[str, Any]:
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
            url = f'https://market.csgo.com/api/v2/my-inventory?key={self._api_key}&lang={lang}',
            method = 'post'
            )

        if status == 200:
            return response 

        return response

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
            url = f'https://market.csgo.com/api/v2/items?key={self._api_key}',
            method = 'post'
        )

        if status == 200:
            return response

        return response

    async def put_item_up_sale(self, item_id: int, price_item: int | float, currency: str ='RUB') -> dict[str, str]:
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
            url = f'https://market.csgo.com/api/v2/add-to-sale?key={self._api_key}&id={item_id}&price={price_item}&cur={currency}',
            method = 'post'
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

    async def update_price_item(self, item_id: int | str, new_price_item: int | float, currency: str ='RUB') -> dict[str, str]:
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
            url = f'https://market.csgo.com/api/v2/set-price?key={self._api_key}&item_id={item_id}&price={new_price_item}&cur={currency}',
            method = 'post'
        )

        if status == 200:
            
            if response['success']:
                return {
                        'status': True,
                        'message': 'Цена изменена'
                        }
            
            return {
                    'status': False,
                    'message': 'Предмет с данным ID не найден'
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
                url = 'https://market.csgo.com/api/v2/prices/RUB.json',
                method = 'get'
            )

            if status == 200:
                return response
            
            return response


import asyncio

async def main():
    m = CSMarket()

    d = await m.get_items_for_sale()

    print(d)

asyncio.run(main())