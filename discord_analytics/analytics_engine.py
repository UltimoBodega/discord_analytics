from typing import Dict

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from libdisc.models.message import Message
from libdisc.models.user import User


class AnalyticsEngine:
    """
    Supplies analytical data for our discord app
    """

    def __init__(self, db_session: Session):
        self.session = db_session


    def get_user_by_char_count(self, channel_id: int) -> Dict[str, int]:
        """
        Get ths total character count for all the users for the specified channel

        @param channel_id:
        @return: Dictionary of {user_name: chracter_count}
        """

        return {user_name: character_count for user_name, character_count in \
                (self.session.query(
                    User.name, func.sum(Message.char_count))
                 .join(Message, Message.user_id == User.id)
                 .filter(Message.channel_id == channel_id)
                 .group_by(User.name))}
