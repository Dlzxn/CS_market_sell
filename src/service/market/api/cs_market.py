import aiohttp
from typing import Any
from .src.config import *


config = Config()


class CSMarket:
    def __init__(self):
        self._api_key = config.api_key

    async def get_inventory_steam(self, lang: str = 'ru') -> dict[str, Any]:
        """
        Получить весь инвентарь Steam~ аккаунта
        * Получаем только те предметы, которые можно выставить на продажу
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=f'https://market.csgo.com/api/v2/my-inventory?key={self._api_key}&lang={lang}'
                ) as response:
                steam_invetory = await response.json()
                return steam_invetory

    async def get_items_for_sale(self) -> dict[str, Any]:
        """
        Получить список предметов, выстравленные на продажу
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=f'https://market.csgo.com/api/v2/items?key={self._api_key}'
                ) as response:
                items = await response.json()
                return items

    async def put_item_up_sale(self, item_id: int, price_item: int | float, currency: str ='RUB') -> dict[str, str]:
        """
        Выставить предмет на продажу
        item_id - id предмета из инвенторя Steam
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=f'https://market.csgo.com/api/v2/add-to-sale?key={self._api_key}&id={item_id}&price={price_item}&cur={currency}'
                ) as response:
            
                res = await response.json()

                if res['success']:
                    return {'message': f'Предмет выставлен на продажу'}
                else:
                    return {'message': res['error']}

    async def update_price_item(self, item_id: int, new_price_item: int | float, currency: str ='RUB') -> dict[str, str]:
        """
        Установить новую цена на предмет
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=f'https://market.csgo.com/api/v2/set-price?key={self._api_key}&item_id={item_id}&price={new_price_item}&cur={currency}'
                ) as response:

                res = await response.json()

                if res['success']:
                    return {'message': 'Цена изменена'}
                else:
                    return {'message': 'Предмет с данным ID не найден'}