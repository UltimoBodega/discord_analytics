from __future__ import annotations

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session

from app_configs.config_manager import ConfigManager
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
        return DB.__instance

    @staticmethod
    def setup_db() -> None:
        """
        Creates the database with all it's table if needed
        @return:
        """
        BaseModel.metadata.create_all(DB.get_instance().engine)

    def __init__(self) -> None:
        """
        Private singleton constructor
        """
        if DB.__instance is not None:
            raise Exception("This class is a singleton")
        else:
            DB.__instance = self


        self.engine = create_engine(ConfigManager.get_instance().get_db_url(), pool_recycle=299, pool_pre_ping=True)
        self.session_factory = sessionmaker(bind=self.engine)

    @contextmanager
    def make_session(self) -> Session:
        """
        Makes a scoped session
        @DB.setup_session
        foo():

        @return: The current active session
        """
        session = scoped_session(self.session_factory)
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.remove()
        return


