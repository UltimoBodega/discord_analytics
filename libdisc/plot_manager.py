import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

from discord_analytics.analytics_engine import StatItem
from scipy.interpolate import make_interp_spline, BSpline

class PlotManager:
    """
    This class serves as the plot generator for any analytics.
    """

    def __init__(self):
        pass

    def prepare_stat_items(self, stat_item:StatItem) -> (StatItem, int, int,
                                                         int, int):
        """
        Pre-process data in a StatItem.

        @param stat_item: StatItem object
        @return: a Tuple with a StatItem object, and min and max values for both:
                 timestamps and values within inputted StatItem.
        """
        all_ts, all_vals = [], []

        for user in stat_item:
            all_ts.extend(stat_item[user].timestamp)
            all_vals.extend(stat_item[user].values)

        if not all_ts:
            return (None, None, None, None, None)

        max_ts, min_ts = int(max(all_ts)), int(min(all_ts))
        max_val, min_val = int(max(all_vals)), int(min(all_vals))

        return (stat_item, max_ts, min_ts, max_val, min_val)


    def generate_trend_image(self, stat_item:StatItem) -> str:
        """
        Generates a trend image based on StatItem.

        @param stat_item: StatItem object
        @return: a filepath/filename to the generated trend image.
        """
        filename = os.getcwd()+'/trend.png'
        (stat_item, max_ts, min_ts, max_val, min_val) = self.prepare_stat_items(stat_item)

        if stat_item is None:
            print("Empty StatItem - Possible no data in DB for discord channel.")
            return ""

        fig = plt.figure(figsize=(8, 6), dpi=300)
        ax = fig.add_subplot(111)

        for user in stat_item:
            try:
                timestamp_smooth = np.linspace(min(stat_item[user].timestamp), max(stat_item[user].timestamp), 300) 
                spl = make_interp_spline(stat_item[user].timestamp, stat_item[user].values, k=3)  # type: BSpline
                values_smooth = spl(timestamp_smooth)
                ax.plot_date(timestamp_smooth, values_smooth, label=user, ls='-', markersize=0)
            except:
                print(f"Not enough trend data for: {user}")
            
        
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
        ax.set_ylabel("Char count")
        ax.set_xlabel("Time")
        ax.set_title("User Trends")
        ax.set_aspect('auto')
        plt.legend()
        plt.grid()
        fig.savefig(filename)
        plt.close()

        return filename