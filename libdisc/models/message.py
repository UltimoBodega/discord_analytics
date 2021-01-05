from typing import Set, Tuple

from sqlalchemy import Column, Integer, ForeignKey, BigInteger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from libdisc.models.base_mixin import Base

class Message(Base):
    """
    Table used to store messages
    """

    __tablename__ = "message"
    __table_args__ = {'mysql_engine':'InnoDB', 'mysql_charset': 'utf8mb4'}
    id = Column(BigInteger, primary_key=True)
    timestamp = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id",
                                         ondelete='cascade',
                                         onupdate='cascade'), nullable=False)
    channel_id = Column(BigInteger, index=True)
    word_count = Column(BigInteger)
    char_count = Column(BigInteger)

    @staticmethod
    def add_message(
            db_session: Session,
            user_id: int,
            channel_id: int,
            timestamp: int,
            word_count: int,
            char_count: int,
            cache: Set[Tuple[int, int]] = None) -> None:

        """
        Adds message into the database
        @param db_session: The current database session
        @param user_id: The id of the user.
        @param channel_id: The id of the channel.
        @param timestamp: Given timestamp
        @param word_count: The word count of the message
        @param char_count: The character count of the message.
        @param cache: Optional cache to determine if the message already exists in the database
        @return: None
        """

        if cache and (user_id, timestamp) in cache:
            return

        message = (db_session.query(Message)
                   .filter(Message.timestamp == timestamp, Message.user_id == user_id)
                   .one_or_none())

        if message is None:
            message = Message(timestamp=timestamp,
                              user_id=user_id,
                              channel_id=channel_id,
                              word_count=word_count,
                              char_count=char_count)
        db_session.add(message)

        try:
            db_session.commit()
            if cache:
                cache.add((user_id, timestamp))
        except SQLAlchemyError:
            db_session.rollback()
            raise
