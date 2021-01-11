from typing import Dict, Tuple
from sqlalchemy import Column, String, UniqueConstraint, Integer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import relationship, backref, Session

from libdisc.dataclasses.discord_objects import DiscordUser
from libdisc.models.base_mixin import BaseModel


class User(BaseModel):
    """
    Table used to describe user entities
    """

    __tablename__ = "user"
    __table_args__ = (UniqueConstraint('name', 'discriminator'),
                      {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'})
    id = Column(Integer, primary_key=True)
    name = Column(String(length=256), server_default='', nullable=False)
    nickname = Column(String(length=256), server_default='', nullable=False)
    discriminator = Column(String(length=256), server_default='', nullable=False)
    messages = relationship("Message", backref=backref("user"))

    @staticmethod
    def get_or_create(db_session: Session,
                      discord_user: DiscordUser,
                      cache: Dict[Tuple[str, str], int] = None) -> int:
        """
        Returns a user's id which it will create if necessary in the DB.

        @param db_session: current database session
        @param discord_user: user to fetch or create
        @param cache: optional cache object to lookup database users
        @return: fetched used id
        """

        user_key = (discord_user.name, discord_user.discriminator)
        if cache and user_key in cache:
            return cache[user_key]

        user = (db_session.query(User)
                .filter(User.name == discord_user.name,
                        User.discriminator == discord_user.discriminator)
                .one_or_none())

        if user is None:
            user = User(name=discord_user.name,
                        nickname=discord_user.nickname,
                        discriminator=discord_user.discriminator)
            db_session.add(user)

            try:
                db_session.commit()
            except SQLAlchemyError:
                db_session.rollback()
                raise

        if cache:
            cache[user_key] = user.id

        return user.id
