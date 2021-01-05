from collections import defaultdict
from typing import Dict, Set, Tuple

from sqlalchemy import desc
from sqlalchemy.orm import Session
from libdisc.models.message import Message
from libdisc.models.user import User


class DatabaseManager:
    """
    Serves as the main database access layer
    """

    def __init__(self, db_session: Session):
        self.session: Session = db_session
        self.user_cache: Dict[str, int] = {}
        self.message_cache: Set[Tuple[int, int]] = set()
        print('Loading caches user and message caches')
        self.load_user_cache()
        self.load_message_cache()
        print(f'User cache size: {len(self.user_cache.items())}')
        print(f'Message cache size: {len(self.message_cache)}')

    def load_message_cache(self) -> None:
        """
        Populates the message cache.
        """
        for user_id, timestamp in self.session.query(Message.user_id, Message.timestamp):
            self.message_cache.add((user_id, timestamp))

    def load_user_cache(self) -> None:
        """
        Populates the user cache.
        """
        for user in self.session.query(User):
            self.user_cache[user.name] = user.id

    def add_new_message(self,
                        user_name: str,
                        timestamp: int,
                        message_channel_id: int,
                        message_word_count: int,
                        message_char_count: int) -> None:
        """
        Inserts message into the db, as well as user if it doesn't exist.
        @param user_name: The message's user name
        @param timestamp: The message's timestamp in unixstimestamp
        @param message_channel_id: The message's channel id
        @param message_word_count: The message's word count
        @param message_char_count: The message's character count
        """

        user_id = User.get_or_create(db_session=self.session,
                                     user_name=user_name,
                                     cache=self.user_cache)
        Message.add_message(db_session=self.session,
                            user_id=user_id,
                            channel_id=message_channel_id,
                            timestamp=timestamp,
                            word_count=message_word_count,
                            char_count=message_char_count,
                            cache=self.message_cache)

    def get_last_message_timestamp(self, message_channel_id: int) -> int:
        """
        Returns the latest timestamp from message from a particular channel
        @param message_channel_id: The message's channel id
        @return: last fetched timestamp of the channel's messages if no messages then 0
        """

        timestamp = (self.session.query(Message.timestamp)
                     .filter(Message.channel_id == message_channel_id)
                     .order_by(desc(Message.timestamp))
                     .first())

        return timestamp[0] if timestamp else 0
