import context  # noqa
from db.db import DB
from libdisc.dataclasses.discord_objects import DiscordUser
from libdisc.models.user import User


def test_user_get_or_create() -> None:
    DB.get_instance().setup_db('sqlite://')
    test_user = DiscordUser("John", "Jonny", "1234")
    with DB.get_instance().make_session() as db_session:
        user_id = User.get_or_create(db_session=db_session,
                                     discord_user=test_user)
        assert user_id is not None
        assert user_id == User.get_or_create(db_session=db_session,
                                             discord_user=test_user)
