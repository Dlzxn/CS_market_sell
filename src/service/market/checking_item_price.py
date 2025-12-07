import json


def checking_item_price(user_id: int, item_id: int, last_price: int | float):
    """
        Summary: Проверка стоимости скина

        Parameters:
            user_id: int - ID пользователя
            item_id: str - название скина
            last_price: int | float - последняя рекомендованная цена маркета
        
        Return:
            Any
    """
    with open('data/checking_item_price.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    if item_id in data:
        if user_id == data[item_id]['user_id']:
            data[item_id] = {
                "value": last_price - 0.01,
                "user_id": user_id,
            }
            with open('data/checking_item_price.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            return 1
        if last_price < data[item_id]["value"]:
            data[item_id] = {
                "value": last_price - 0.01,
                "user_id": user_id,
            }
            with open('data/checking_item_price.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            return 1
        else:
            return 0

    else:
        data[item_id] = {
            "value": last_price - 0.01,
            "user_id": user_id,
        }
        with open('data/checking_item_price.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        return 1
