# from db import fs_db
# import time
# from datetime import datetime, timezone
# from libdisc.finance_manager import FinanceManager
# from libdisc.database_manager import DatabaseManager
# from libdisc.plot_manager import PlotManager
# from libdisc.dataclasses.discord_objects import DiscordUser, StockItem

# import pprint
# import yfinance as yf  # type: ignore
# import app_configs.config_manager as app_conf

# finance_manager = FinanceManager()
# database_manager = DatabaseManager()
# plot_manager = PlotManager()
# pp = pprint.PrettyPrinter(indent=4)


# def main():
#     # Use the application default credentials
#     app_conf.user_input()
#     fs_db.init_fs_db()
#     # query_symbols = ['MSFT']
#     # day_limit = 10
#     # sec_in_day = 60 * 60 * 24
#     # from_ts = datetime.now(timezone.utc).timestamp() - sec_in_day * day_limit
#     # stats_item = database_manager.get_stock_history(symbols=query_symbols,
#     #                                                 from_ts=from_ts)
#     # print(stats_item['MSFT'].timestamps[:10])
#     # stats_item['MSFT'].timestamps = stats_item['MSFT'].timestamps[:10]
#     # stats_item['MSFT'].values = stats_item['MSFT'].values[:10]
#     # filename = plot_manager.generate_trend_image(
#     #     chart_title='Stock Trends',
#     #     x_label='Date',
#     #     y_label='$',
#     #     stat_item=stats_item)
#     item = finance_manager.get_stock_item('BTC')
#     print(item)


# if __name__ == '__main__':
#     main()
