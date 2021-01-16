from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseModel(Base):  # type: ignore
    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
