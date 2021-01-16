from __future__ import annotations

from contextlib import contextmanager
from typing import Optional, Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from libdisc.models.base_mixin import BaseModel


class DB:
    __instance = None

    @staticmethod
    def get_instance() -> DB:
        """
        Gets singleton class of DB
        @return: a DB
        """
        if DB.__instance is None:
            DB()
        assert DB.__instance
        return DB.__instance

    def __init__(self) -> None:
        """
        Private singleton constructor
        """
        if DB.__instance is not None:
            raise Exception("This class is a singleton")
        else:
            DB.__instance = self

        self.engine: Optional[Engine] = None
        self.session_factory: Optional[sessionmaker] = None

    def setup_db(self, db_url: str) -> None:
        """
        Creates the database with all it's table if needed
        """
        self.engine = create_engine(db_url,
                                    pool_recycle=299,
                                    pool_pre_ping=True)
        BaseModel.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(bind=self.engine)

    @contextmanager
    def make_session(self) -> Generator[Session, None, None]:
        """
        Makes a scoped session
        @DB.setup_session
        foo():

        @return: The current active session
        """
        session = scoped_session(self.session_factory)
        try:
            yield session
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.remove()
        return
