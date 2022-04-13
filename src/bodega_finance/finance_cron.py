
import schedule  # type: ignore
import time
import app_configs.config_manager as app_conf
import threading

from datetime import datetime, timezone
from libdisc.finance_manager import FinanceManager
from libdisc.database_manager import DatabaseManager


app_conf.user_input()
finance_manager = FinanceManager()
database_manager = DatabaseManager()
REFRESH = 120
tick = 0
# ------------- Main Program ------------- #


def main():
    database_manager.start_fs()
    schedule.every(REFRESH).seconds.do(fetch)
    fetch()
    while True:
        schedule.run_pending()
        time.sleep(1)


def fetch():
    global tick
    tick += 1
    print(f'tick: {tick}')
    print(f'thread count: {threading.active_count()}')
    try:
        print('-----FETCH START-----')
        symbols = database_manager.get_all_tracking_symbols()
        print(f'Symbols: {symbols}')
        stock_items = finance_manager.get_stock_item_concurrent(symbols)

        for item in stock_items.values():
            if not finance_manager.check_valid_stock(item):
                print(f'Invalid stock symbol: {item.symbol}')
                continue
            print(item)
            timestamp_now = datetime.now(timezone.utc).timestamp()
            database_manager.add_stock_entry(timestamp=timestamp_now, item=item)
        print('-----FETCH END-----\n')
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
