from typing import Dict

from sqlalchemy import func

from db.db import DB
from libdisc.models.message import Message
from libdisc.models.user import User


class AnalyticsEngine:
    """
    Supplies analytical data for our discord app
    """

    def __init__(self) -> None:
        pass

    def get_user_by_char_count(self, channel_id: int) -> Dict[str, int]:
        """
        Get ths total character count for all the users for the specified channel

        @param channel_id:
        @return: Dictionary of {user_name: chracter_count}
        """
        with DB.get_instance().make_session() as  db_session:
            return {user_name: character_count for user_name, character_count in \
                    (db_session.query(
                        User.name, func.sum(Message.char_count))
                     .join(Message, Message.user_id == User.id)
                     .filter(Message.channel_id == channel_id)
                     .group_by(User.name))}
