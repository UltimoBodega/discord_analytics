import os
from typing import Dict, Tuple, Optional, List, Union

import matplotlib.dates as mdates  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import numpy as np  # type: ignore
from scipy.interpolate import make_interp_spline, BSpline  # type: ignore

from libdisc.dataclasses.discord_objects import StatItem


class PlotManager:
    """
    This class serves as the plot generator for any analytics.
    """

    def __init__(self):
        pass

    def _prepare_stat_items(self,
                            stat_item: Optional[Dict[str, StatItem]]) -> Tuple[int, int, int, int]:
        """
        Pre-process data in a StatItem.

        @param stat_item: StatItem object
        @return: a Tuple with a StatItem object, and min and max values for
        both: timestamps and values within inputted StatItem.
        """
        all_ts: List[Union[int, float]] = list()
        all_vals: List[Union[int, float]] = list()

        if stat_item is None or not stat_item:
            return 0, 0, 0, 0

        for user in stat_item.keys():
            all_ts.extend(stat_item[user].timestamps)
            all_vals.extend(stat_item[user].values)

        max_ts, min_ts = int(max(all_ts)), int(min(all_ts))
        max_val, min_val = int(max(all_vals)), int(min(all_vals))

        return max_ts, min_ts, max_val, min_val

    def generate_trend_image(self,
                             chart_title: str,
                             x_label: str,
                             y_label: str,
                             stat_item: Optional[Dict[str, StatItem]]) -> str:
        """
        Generates a trend image based on StatItem.

        @param stat_item: StatItem object
        @return: a filepath/filename to the generated trend image.
        """
        filename = os.getcwd() + '/trend.png'
        # (max_ts, min_ts, max_val, min_val) = \
        # self._prepare_stat_items(stat_item)

        if stat_item is None:
            print("Empty StatItem - Possible no data in DB for discord channel.")
            return ""

        fig = plt.figure(figsize=(8, 6), dpi=300)
        ax = fig.add_subplot(111)

        for key in stat_item:
            try:
                timestamps_smooth = np.linspace(min(stat_item[key].timestamps),
                                                max(stat_item[key].timestamps),
                                                300)
                spl = make_interp_spline(stat_item[key].timestamps,
                                         stat_item[key].values,
                                         k=3)  # type: BSpline
                values_smooth = spl(timestamps_smooth)
                ax.plot_date(timestamps_smooth, values_smooth, label=key,
                             ls='-', markersize=0)
            except ValueError:
                print(f"Not enough trend data to smooth: {key}")
                ax.plot_date(stat_item[key].timestamps,
                             stat_item[key].values,
                             label=key,
                             ls='-',
                             markersize=0)

        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
        ax.set_title(chart_title)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_aspect('auto')
        plt.legend()
        plt.grid()
        fig.savefig(filename)
        plt.close()

        return filename
