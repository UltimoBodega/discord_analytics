import numpy as np  # type: ignore
from typing import Dict
from collections import defaultdict
from sqlalchemy import func, asc

from db.db import DB
from libdisc.models.message import Message
from libdisc.models.user import User
from libdisc.dataclasses.discord_objects import StatItem


class AnalyticsEngine:
    """
    Supplies analytical data for our discord app
    """

    def __init__(self) -> None:
        pass

    def get_user_by_char_count(self, channel_id: int, from_timestamp: int = 0) -> Dict[str, int]:
        """
        Get ths total character count for all the users for
        the specified channel

        @param channel_id: desired channel id to pull from.
        @param from_timestamp: count messages starting from from_timestamp, entire history will be counted.
        @return: Dictionary of {user_name: character_count}
        """
        with DB.get_instance().make_session() as db_session:
            return {user_name: character_count for user_name, character_count in
                    (db_session.query(
                        User.name, func.sum(Message.char_count))
                     .join(Message, Message.user_id == User.id)
                     .filter(Message.channel_id == channel_id)
                     .filter(Message.timestamp >= from_timestamp)
                     .group_by(User.name))}

    def get_stats_grouped_by_time(self, channel_id: int, filter_ts=0) -> Dict[
            str, StatItem]:
        """
        Groups stats by weekly intervals.

        @param channel_id: The Discord channel id number.
        @param filter_ts: Timestamp to use for filtering.
        @return: Dictionary of {str: StatItem}
        """
        out_dict: Dict[str, StatItem] = defaultdict(lambda: StatItem())
        sec_in_week = 60 * 60 * 24 * 7
        with DB.get_instance().make_session() as db_session:
            query = (
                db_session.query(
                    User.name,
                    # hack that compensates for SQLite not
                    # having FLOOR function
                    func.round((Message.timestamp / sec_in_week) - 0.5).label("day_time"),
                    func.sum(Message.char_count))
                .join(Message, Message.user_id == User.id)
                .filter(Message.channel_id == channel_id)
                .filter(Message.timestamp > filter_ts)
                .group_by(User.name, "day_time")
                .order_by(asc("day_time")))

        for name, timestamps, character_count in query:
            if "bot" in name:
                continue
            out_dict[name].timestamps.append(np.multiply(timestamps, 7))
            out_dict[name].values.append(character_count)

        return out_dict
