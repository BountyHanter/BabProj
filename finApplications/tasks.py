import time

from finApplications.ByBit import get_average_price


def run_task():
    while True:
        get_average_price()
        time.sleep(60)  # Ждем 60 секунд перед следующим запуском
