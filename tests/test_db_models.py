import context
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from libdisc.models.base_mixin import Base
from libdisc.models.gif import Gif
from libdisc.models.user import User
from libdisc.models.message import Message

dbpath='sqlite:///gif.db'
engine = create_engine(dbpath, pool_recycle=600)
Base.metadata.create_all(engine)
curr_session = sessionmaker(bind=engine)()

# people = ["demmy", "cris", "juan", "ulises", "wang"]
people = ["ulises"]

for person in people:
    user_id = User.get_or_create(curr_session, person)
    timestamp = Gif.read_gif_entry(curr_session, user_id)
    print(timestamp)