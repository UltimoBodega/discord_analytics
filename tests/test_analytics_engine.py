from typing import List

from db.db import DB
from discord_analytics.analytics_engine import AnalyticsEngine
from libdisc.database_manager import DatabaseManager
from libdisc.dataclasses.discord_objects import DiscordUser


def _get_sample_users() -> List[DiscordUser]:
    return [DiscordUser("John", "Jonny", "1234"),
            DiscordUser("Jane", "Jenny", "4312"),
            DiscordUser("Bob", "Bobby", "3134"),
            DiscordUser("Michael", "Mike", "2312")]


def test_db_analytics_user_char_count() -> None:
    sample_users = _get_sample_users()
    DB.get_instance().setup_db('sqlite://')
    analytics_engine = AnalyticsEngine()
    database_manager = DatabaseManager()
    channel_id = 0
    for i, user in enumerate(sample_users):
        database_manager.add_new_message(discord_user=user,
                                         timestamp=i,
                                         message_channel_id=channel_id,
                                         message_char_count=i * 10,
                                         message_word_count=i * 20)

    result = analytics_engine.get_user_by_char_count(channel_id)

    assert result == {'John': 0, 'Jane': 10, 'Bob': 20, 'Michael': 30}

    result = analytics_engine.get_user_by_char_count(channel_id, 2)

    assert result == {'Bob': 20, 'Michael': 30}

# def test_db_analytics(dbpath,channel_id,output) -> None:
#     try:
#         DB.get_instance().setup_db(dbpath)
#         analytics_engine = AnalyticsEngine()
#         result = analytics_engine.get_stats_grouped_by_time(channel_id)
#     except Exception as error_msg:
#         result = error_msg


#     filename = PlotManager().generate_trend_image(result)
#     print(filename)
#     assert(str(result) == output)
