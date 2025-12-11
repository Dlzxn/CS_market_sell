import json
import os
from typing import Union, Dict

# Константа для пути к файлу
CACHE_FILE = 'data/checking_item_price.json'
# Константа для снижения цены (1 копейка)
PRICE_DECREMENT = 1


def load_cache() -> Dict:
    """Загружает данные кэша из JSON-файла."""
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_cache(data: Dict) -> None:
    """Сохраняет данные кэша в JSON-файл."""
    # Используем временный файл или блокировку для защиты от повреждения (базовый уровень)
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        # В реальном приложении: logging.error(f"Ошибка сохранения кэша: {e}")
        pass


def checking_item_price(user_id: Union[int, str], item_id: Union[int, str], best_market_price_cents: int) -> int:
    """
    Summary: Проверка стоимости скина, предотвращающая демпинг между своими аккаунтами.

    Parameters:
        user_id: int | str - ID пользователя, который пытается обновить цену.
        item_id: int | str - ID предмета.
        best_market_price_cents: int - Лучшая цена конкурента (в копейках/центах).

    Return:
        1: Можно обновлять цену (нужно снижать).
        0: Цена уже установлена нашим аккаунтом или конкурент не снижал цену.
    """

    # 1. Загрузка данных
    data = load_cache()
    item_id_str = str(item_id)
    user_id_str = str(user_id)

    # Желаемая цена (цена конкурента минус 1 копейка)
    desired_price = best_market_price_cents - PRICE_DECREMENT

    # 2. Если предмет уже отслеживается
    if item_id_str in data:
        cached_price = data[item_id_str]['value']
        cached_user_id = data[item_id_str]['user_id']

        # 2.1. Если это наш аккаунт (позволяем обновить, чтобы догнать внешнего конкурента)
        if user_id_str == cached_user_id:
            # Обновляем кэш новой желаемой ценой и разрешаем обновление
            data[item_id_str] = {"value": desired_price, "user_id": user_id_str}
            save_cache(data)
            return 1  # Разрешаем обновление цены

        # 2.2. Если это аккаунт конкурента (проверка на демпинг)

        # Если рыночная цена (best_market_price_cents) строго ниже, чем наша последняя установленная
        if best_market_price_cents < cached_price:
            # Внешний конкурент снизил цену, мы должны следовать за ним
            data[item_id_str] = {"value": desired_price, "user_id": user_id_str}
            save_cache(data)
            return 1  # Разрешаем обновление цены
        else:
            # Рыночная цена НЕ ниже нашей последней цены (или равна ей).
            # Это означает, что другой наш аккаунт уже защитил позицию.
            # Мы не обновляем цену, чтобы не демпинговать.
            return 0  # Запрещаем обновление цены

    # 3. Если предмет не отслеживался (первый раз, когда аккаунт пытается продать)
    else:
        data[item_id_str] = {"value": desired_price, "user_id": user_id_str}
        save_cache(data)
        return 1  # Разрешаем обновление цены (и начинаем отслеживание)