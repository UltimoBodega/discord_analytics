from sqlalchemy.ext.declarative import declared_attr

class Base(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base(cls=Base)