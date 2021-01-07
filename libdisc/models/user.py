
from typing import Dict
from sqlalchemy import Column, String, UniqueConstraint, Integer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import relationship, backref, Session

from libdisc.models.base_mixin import BaseModel


class User(BaseModel):
    """
    Table used to describe user entities
    """

    __tablename__ = "user"
    __table_args__ = (UniqueConstraint('name'), {'mysql_engine':'InnoDB', 'mysql_charset': 'utf8mb4'})
    id = Column(Integer, primary_key=True)
    name = Column(String(length=256), server_default='', nullable=False)
    messages = relationship("Message", backref=backref("user"))


    @staticmethod
    def get_or_create(db_session: Session, user_name: str,  cache: Dict[str, int] = None) -> int:
        """
        Returns a user which it will create if necessary in the DB.

        @param db_session: current database session
        @param user_name: user name to fetch or create
        @param cache: optional cache object to lookup database users
        @return: fetched used id
        """

        if cache and user_name in cache:
            return cache[user_name]

        user = (db_session.query(User)
                .filter(User.name == user_name)
                .one_or_none())

        if user is None:
            user = User(name=user_name)
        db_session.add(user)

        try:
            db_session.commit()
            if cache:
                cache[user_name] = user.id
        except SQLAlchemyError:
            db_session.rollback()
            raise

        return user.id
