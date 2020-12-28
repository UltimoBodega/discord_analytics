from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, desc, func, exc #, asc, and_
from sqlalchemy.orm import relationship, backref, Session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    user_id = Column(Integer, primary_key=True)
    name = Column(String)
    messages = relationship("Message", backref=backref("user"))

class Message(Base):
    __tablename__ = "message"
    message_id = Column(Integer, primary_key=True)
    timestamp = Column(String)
    user_id = Column(Integer, ForeignKey("user.user_id"))
    channel_id = Column(Integer)
    words_pd = Column(Integer)
    chars_pd = Column(Integer)

class StatsDB():
    """
    TODO
    """

    def __init__(self, db_name='message.db'):
        engine = create_engine('sqlite:///'+db_name)
        Base.metadata.create_all(engine)
        Session = sessionmaker()
        Session.configure(bind=engine)
        self.session = Session()

    def add_new_message(self, user_name, message_channel_id, message_timestamp, message_words, message_chars):
        """
        Inserts Message object to db
        """
        user = (self.session.query(User)
                .filter(User.name == user_name)
                .one_or_none())

        if user is None:
            user = User(name=user_name)
            self.session.add(user)

        message = (self.session.query(Message)
                   .filter(Message.timestamp == message_timestamp, Message.user_id == user.user_id)
                   .one_or_none())

        if message is None:
            message = Message(channel_id = message_channel_id,
                              timestamp=message_timestamp,
                              words_pd=message_words,
                              chars_pd=message_chars)
            message.user=user
            self.session.add(message)

        try:
            self.session.commit()
        except exc.SQLAlchemyError:
            self.session.rollback()
            print('Failed to commit')
            raise

    def fetch_last_timestamp(self, message_channel_id):
        """
        Returns the latest timestamp from message from a particular channel
        """
        last_ts = None
        message = (self.session.query(Message)
                   .filter(Message.channel_id == message_channel_id)
                   .order_by(desc("timestamp"))
                   .first())

        if message is not None:
            last_ts = message.timestamp
        
        return last_ts

    def sum_user_chars(self, user_name, channel_id):
        """
        Sums total number of chars per user
        """
        user = (self.session.query(User)
                .filter(User.name == user_name)
                .one_or_none())

        if user is None:
            return

        qry = (self.session.query(func.sum(Message.chars_pd))
               .filter(Message.user_id == user.user_id, Message.channel_id == message_channel_id)
               .first())

        return qry[0]

    def get_all_users(self):
        """
        Returns list of User objects
        """

        users = self.session.query(User).all()

        return users