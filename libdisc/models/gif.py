from typing import Tuple, Dict
from sqlalchemy import Column, String, UniqueConstraint, Integer, ForeignKey, BigInteger
from libdisc.models.base_mixin import Base
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

class Gif(Base):
    """
    Table used to describe Gifs for users
    """

    __tablename__ = "gif"
    __table_args__ = (UniqueConstraint('user_id'), {'mysql_engine':'InnoDB', 'mysql_charset': 'utf8mb4'})
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id",
                                         ondelete='cascade',
                                         onupdate='cascade'), nullable=False)
    keyword = Column(String(length=256), server_default='', nullable=False)
    timestamp = Column(BigInteger, server_default='0', nullable=False)

    @staticmethod
    def upsert_gif_entry(db_session: Session, user_id: int, keyword: str, 
                         timestamp:int, cache: Dict[int, Tuple[str, int]]=None) -> None:
        """
        Updates or creates a gif entry for a user in the DB.

        @param db_session: The current database session
        @param user_id: The id of the user
        @param keyword: The Gif keyword string to be user for the API query
        @param timestamp: The latest timestamp corresponding to when the bot posted a Gif for user_id
        @param cache: Optional cache object to lookup database users
        @return: None
        """

        gif = db_session.query(Gif).\
            filter(Gif.user_id == user_id).one_or_none()

        if gif is None:
            db_session.add(Gif(user_id=user_id, keyword=keyword, timestamp=timestamp))
        else:
            db_session.query(Gif).\
            filter(Gif.user_id == user_id).\
            update({"keyword": keyword, "timestamp": timestamp})

        try:
            db_session.commit()
            if cache:
                cache[user_id] = (keyword, timestamp)
        except SQLAlchemyError:
            db_session.rollback()
            raise

    @staticmethod
    def read_gif_preference(db_session: Session, user_id:int,  cache: Dict[int, Tuple[str, int]] = None) -> Tuple[str, int]:
        """
        Reads the latest timestamp for a user in the DB.

        @param db_session: The current database session
        @param user_id: The id of the user
        @param cache: Optional cache object to lookup database users
        @return: Tuple with The Gif keyword string to be user for the API query and
                 the latest timestamp corresponding to when the bot posted a Gif for user_id
        """
        timestamp = 0
        keyword = ""
        if cache and user_id in cache:
            return cache[user_id]

        gif = (db_session.query(Gif)
                .filter(Gif.user_id == user_id)
                .one_or_none())

        if gif is not None:
            timestamp = gif.timestamp
            keyword = gif.keyword

        return (keyword, timestamp)