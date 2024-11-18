from finApplications.ByBit import take_bybit_data


def get_bybit_price():
    bybit_data = take_bybit_data()
    # Получение текущего курса и времени замера курса из профиля пользователя
    current_course = bybit_data['average_price']
    return current_course


def get_bybit_time():
    bybit_data = take_bybit_data()
    current_time = bybit_data['time']
    return current_time
