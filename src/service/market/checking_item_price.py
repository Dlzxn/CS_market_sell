def checking_item_price(user_id: int, item_id: int, currently_price: int | float):
    """
        Summary: Проверка стоимости скина

        Parameters:
            user_id: int - ID пользователя
            item_id: str - название скина
            currently_price: int | float - текущая цена
        
        Return:
            Any
    """

    with open('data/checking_item_price.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    
    if item_id in data:
        user = data[item_id]['user']

        if user == user_id:
            return 'Надо поменять цену скина'

        else:
            price = data[item_id]['price']

            if currently_price > price:
                return f'Надо поменять цена на {price + 0.01}'

            return 'Наша цена самая маленькая'

    return 'Скина нет'