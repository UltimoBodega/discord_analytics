from typing import Dict, Set, Tuple, List, Callable, Any

from sqlalchemy import desc

from db.db import DB
from db import fs_db
from firebase_admin import firestore  # type: ignore
from libdisc.dataclasses.discord_objects import (DiscordUser, StockItem,
                                                 AlertItem, StatItem)
from libdisc.models.message import Message
from libdisc.models.user import User
from libdisc.models.gif import Gif


class DatabaseManager:
    """
    Serves as the main database access layer
    """

    def __init__(self) -> None:
        self.user_cache: Dict[Tuple[str, str], int] = {}
        self.message_cache: Set[Tuple[int, int, int]] = set()
        self.gif_cache: Dict[int, Tuple[str, int]] = {}
        self.history_watch = None

    def start_fs(self) -> None:
        fs_db.init_fs_db()

    def load_cache(self) -> None:
        """
        Loads all caches
        @return: None
        """
        with DB.get_instance().make_session() as db_session:
            # Message cache
            for user_id, channel_id, timestamp in db_session.query(Message.user_id,
                                                                   Message.channel_id,
                                                                   Message.timestamp):
                self.message_cache.add((user_id, channel_id, timestamp))
            # User cache
            for user in db_session.query(User):
                self.user_cache[(user.name, user.discriminator)] = user.id
            # Gif cache
            for gif in db_session.query(Gif):
                self.gif_cache[gif.user_id] = (gif.keyword, gif.timestamp)

        print(f'User cache size: {len(self.user_cache.items())}')
        print(f'Message cache size: {len(self.message_cache)}')
        print(f'Gif cache size: {len(self.gif_cache)}')

    def reset_cache(self) -> None:
        """
        Resets both user and message caches
        """
        self.user_cache.clear()
        self.message_cache.clear()
        self.gif_cache.clear()

    def add_new_message(self,
                        discord_user: DiscordUser,
                        timestamp: int,
                        message_channel_id: int,
                        message_word_count: int,
                        message_char_count: int) -> None:
        """
        Inserts message into the db, as well as user if it doesn't exist.
        @param discord_user: The message's user.
        @param timestamp: The message's timestamp in unix-timestamp.
        @param message_channel_id: The message's channel id.
        @param message_word_count: The message's word count.
        @param message_char_count: The message's character count.
        """
        with DB.get_instance().make_session() as db_session:
            user_id = User.get_or_create(db_session=db_session,
                                         discord_user=discord_user,
                                         cache=self.user_cache)
            Message.add_message(db_session=db_session,
                                user_id=user_id,
                                channel_id=message_channel_id,
                                timestamp=timestamp,
                                word_count=message_word_count,
                                char_count=message_char_count,
                                cache=self.message_cache)

    def get_last_message_timestamp(self, message_channel_id: int) -> int:
        """
        Returns the latest timestamp from message from a particular channel.

        @param message_channel_id: The message's channel id
        @return: last fetched timestamp of the channel's messages
        if no messages then 0
        """
        with DB.get_instance().make_session() as db_session:
            timestamp = (db_session.query(Message.timestamp)
                         .filter(Message.channel_id == message_channel_id)
                         .order_by(desc(Message.timestamp))
                         .first())

            return timestamp[0] if timestamp else 0

    def get_last_gif_preference(self,
                                discord_user: DiscordUser) -> Tuple[str, int]:
        """
        Returns the latest Gif preference for a particular user.

        @param discord_user: The Discord user for the Gif preference.
        @return: Tuple with The Gif keyword string to be user for the
        API query and the latest timestamp corresponding to when the bot
        posted a Gif for user_id
        """
        with DB.get_instance().make_session() as db_session:
            user_id = User.get_or_create(db_session=db_session,
                                         discord_user=discord_user,
                                         cache=self.user_cache)

            (keyword, timestamp) = Gif.read_gif_preference(db_session=db_session,
                                                           user_id=user_id,
                                                           cache=self.gif_cache)

            return keyword, timestamp

    def upsert_new_gif_entry(self, discord_user: DiscordUser, keyword: str, timestamp: int = 0) -> None:
        """
        Updates or creates a gif entry for a user in the DB.

        @param discord_user: The Discord user name for the Gif preference.
        @param keyword: The Gif keyword string to be user for the API query
        @param timestamp: The latest timestamp corresponding to when the
        bot posted a Gif for user_id
        @return: None
        """
        with DB.get_instance().make_session() as db_session:
            user_id = User.get_or_create(db_session=db_session,
                                         discord_user=discord_user,
                                         cache=self.user_cache)

            Gif.upsert_gif_entry(db_session=db_session,
                                 user_id=user_id,
                                 keyword=keyword,
                                 timestamp=timestamp,
                                 cache=self.gif_cache)

    def add_stock_alert(self,
                        discord_user: DiscordUser,
                        timestamp: float,
                        channel_id: int,
                        symbol: str,
                        low: int,
                        high: int,
                        note: str) -> None:
        """
        Adds an alert for symbol.

        :param discord_user: The alert setter user
        :param timestamp: message's timestamp
        :param channel_id: message's channelId
        :param symbol: stock symbol to track
        :param low: lower boundry for alert to trigger
        :param high: upper boundry for alert to trigger
        :param note: note to print when alert triggers
        """

        db_ref = fs_db.get_fs_db()
        db_ref.collection(u'alerts').add(
            {
                u'user_id': discord_user.name + discord_user.discriminator,
                u'timestamp': timestamp,
                u'channel_id': channel_id,
                u'symbol': symbol,
                u'low': low,
                u'high': high,
                u'note': note
            }
        )

    def add_stock_track(self,
                        symbol: str) -> None:
        """
        Add stock to track for finance bot.
        :param symbol: stock symbol
        """
        db_ref = fs_db.get_fs_db()
        db_ref.collection(u'tracking').add(
            {
                u'symbol': symbol,
            }
        )

    def add_stock_entry(self,
                        timestamp: int,
                        item: StockItem) -> None:
        """
        Add stock entry to history table
        :param item: stock item
        """
        db_ref = fs_db.get_fs_db()
        db_ref.collection(u'history').add(
            {
                u'timestamp': timestamp,
                u'symbol': item.symbol,
                u'day_low': item.price_day_low,
                u'day_high': item.price_day_high,
                u'price': item.price
            }
        )

    def get_all_tracking_symbols(self) -> List[str]:
        """
        :return: a list of all tracking symbols
        """
        db_ref = fs_db.get_fs_db()
        docs = db_ref.collection(u'tracking').stream()
        out = []
        for d in docs:
            d = d.to_dict()
            out.append(d[u'symbol'])
        return out

    def init_history_watch(self, func: Callable[[StockItem, AlertItem], bool]) -> None:
        db_ref = fs_db.get_fs_db()

        def on_snapshot(col_snapshot, changes, read_time):
            for doc in col_snapshot:
                history_info = doc.to_dict()
                stock_item = StockItem(
                    price=history_info['price'],
                    price_day_low=history_info['day_low'],
                    price_day_high=history_info['day_high'],
                    symbol=history_info['symbol'])
                alerts = self.find_matching_alerts(stock_item)
                for alert in alerts:
                    alert_info = alert.to_dict()
                    print(f'Found alert: {alert_info}')
                    alert_item = AlertItem(
                        timestamp=alert_info['timestamp'],
                        channel_id=alert_info['channel_id'],
                        low=alert_info['low'],
                        high=alert_info['high'],
                        symbol=alert_info['symbol'],
                        note=alert_info['note'])
                    if not func(stock_item, alert_item):
                        print('func fall failed, not deleting alert')
                        return
                    print(f'Deleting {alert.id}')
                    db_ref.collection(u'alerts').document(alert.id).delete()

        self.history_watch = (db_ref.collection(u'history')
                              .order_by(u'timestamp', direction=firestore.Query.DESCENDING)
                              .limit(1)
                              .on_snapshot(on_snapshot))

    def find_matching_alerts(self, item: StockItem) -> List[Any]:
        """
        Alert if stock is less than low or more than high
        :param item: _description_
        :return: _description_
        """
        db_ref = fs_db.get_fs_db()
        out: Any = []
        alert_ref = (db_ref.collection(u'alerts')
                     .where(u'symbol', u'==', item.symbol)
                     .where(u'low', u'>', item.price))

        out.extend(doc for doc in alert_ref.stream())

        alert_ref = (db_ref.collection(u'alerts')
                     .where(u'symbol', u'==', item.symbol)
                     .where(u'high', u'<', item.price))

        out.extend(doc for doc in alert_ref.stream())

        return out

    def get_stock_history(self,
                          symbols: List[str],
                          from_ts: float) -> Dict[str, StatItem]:
        """
        Gets history for all stock symbols
        :param symbol: _description_
        :return: _description_
        """
        db_ref = fs_db.get_fs_db()
        out = {}
        for sym in symbols:
            item = StatItem()
            hist_ref = (
                db_ref.collection(u'history')
                .where(u'timestamp', u'>=', from_ts)
                .where(u'symbol', u'==', sym))
            for entry in hist_ref.stream():
                info = entry.to_dict()
                item.timestamps.append(int(info['timestamp'])/(3600*24))
                item.values.append(int(info['price']))
            out[sym] = item

        return out
