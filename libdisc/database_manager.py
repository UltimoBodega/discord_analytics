from typing import Dict, Set, Tuple

from sqlalchemy import desc

from db.db import DB
from libdisc.dataclasses.discord_objects import DiscordUser
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

    def load_cache(self) -> None:
        """
        Loads all caches
        @return: None
        """
        with DB.get_instance().make_session() as db_session:
            # Message cache
            for user_id, channel_id, timestamp in db_session.query(
                    Message.user_id, Message.channel_id, Message.timestamp):
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

            (keyword, timestamp) = Gif.read_gif_preference(
                db_session=db_session,
                user_id=user_id,
                cache=self.gif_cache)

            return keyword, timestamp

    def upsert_new_gif_entry(self, discord_user: DiscordUser, keyword: str,
                             timestamp: int = 0) -> None:
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
