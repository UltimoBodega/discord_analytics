import yfinance as yf  # type: ignore
import threading
import queue

from libdisc.dataclasses.discord_objects import StockItem
from typing import List, Dict

PRICE_KEY = 'regularMarketPrice'
HIGH_DAY_KEY = 'regularMarketDayHigh'
LOW_DAY_KEY = 'regularMarketDayLow'
WORKER_THREADS = 20


class FinanceManager:
    """
    Serves financial data
    """

    def __init__(self):
        pass

    def check_valid_stock(self, item: StockItem) -> bool:
        return item.price is not None and item.price != -1

    def get_stock_item(self, symbol: str) -> StockItem:
        """
        It takes roughly 10 seconds to fetch a symbol.
        @param symbol: stock symbol
        @return: a stock item containing stock info
        """

        info = yf.Ticker(symbol).info
        return StockItem(
            symbol=symbol,
            price=info[PRICE_KEY] if PRICE_KEY in info else -1,
            price_day_low=info[LOW_DAY_KEY] if LOW_DAY_KEY in info else -1,
            price_day_high=info[HIGH_DAY_KEY] if HIGH_DAY_KEY in info else -1,
        )

    def get_stock_item_concurrent(self,
                                  symbol_list: List[str]) -> Dict[str, StockItem]:
        """
        Fetches all symbols from symbol_list in parallel. Speeding
        it up considerably.
        @param symbol_list: list of symbols to process
        @return: a dictionary of {sym: StockItem}
        """
        q: queue.Queue = queue.Queue()
        stock_dict = {}

        def worker():
            try:
                while True:
                    symbol = q.get(True, .5)
                    try:
                        stock_dict[symbol] = self.get_stock_item(symbol)
                    except Exception as e:
                        print(e)
                    finally:
                        q.task_done()
            except queue.Empty:
                pass

        for i in range(WORKER_THREADS):
            threading.Thread(target=worker, daemon=True).start()

        for symbol in symbol_list:
            q.put(symbol)

        # Block until all tasks are done.
        q.join()

        return stock_dict
