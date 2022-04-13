from db.db import DB
from discord_analytics.analytics_engine import AnalyticsEngine
from libdisc.database_manager import DatabaseManager
from libdisc.dataclasses.discord_objects import DiscordUser
from libdisc.discord_manager import DiscordManager
from libdisc.media_manager import MediaManager
from libdisc.plot_manager import PlotManager
from libdisc.finance_manager import FinanceManager


def test_gif_workflow() -> None:
    """
    Tests the 'upsert' and 'get' method of the Gif class.

    Test procedure:
    1- Reads empty db.
    2- Inserts data to empty db using upsert.
    3- Reads db.
    4- Updates data to db using upsert.
    5- Reads updated db.
    """
    users = [DiscordUser("John", "Jonny", "1234"),
             DiscordUser("Jane", "Jenny", "4312"),
             DiscordUser("Bob", "Bobby", "3134"),
             DiscordUser("Michael", "Mike", "2312")]
    preferences = [(users[0], "Matrix", 150),
                   (users[1], "The Notebook", 150000),
                   (users[2], "Stranger Things", 0),
                   (users[3], "Iron Man", 10000)]
    result = {}
    select_person = users[2]
    update_data = (select_person, "Twin Peaks", 75000)
    output = {'Read empty': ('', 0),
              'Initial preference': ('Stranger Things', 0),
              'Read update': ('Twin Peaks', 75000)}

    DB.get_instance().setup_db("sqlite://")
    analytics_engine = AnalyticsEngine()
    database_manager = DatabaseManager()
    plot_manager = PlotManager()
    finance_manager = FinanceManager()
    media_manager = MediaManager("")
    discord_manager = DiscordManager(db_manager=database_manager,
                                     analytics_engine=analytics_engine,
                                     media_manager=media_manager,
                                     plot_manager=plot_manager,
                                     finance_manager=finance_manager)

    # Query empty DB for Bob - should return nothing
    result["Read empty"] = \
        discord_manager.db_manager.get_last_gif_preference(select_person)
    # discord_manager.db_manager.upsert_new_gif_entry()

    for preference in preferences:
        (user_name, keyword, timestamp) = preference
        discord_manager.db_manager.upsert_new_gif_entry(user_name,
                                                        keyword,
                                                        timestamp)

    # Read for Bob - should initial preference
    result["Initial preference"] = discord_manager.db_manager.get_last_gif_preference(select_person)

    # Update Bob's preferences
    (user_name, keyword, timestamp) = update_data
    discord_manager.db_manager.upsert_new_gif_entry(user_name,
                                                    keyword,
                                                    timestamp)

    # Read for Bob - should initial preference
    result["Read update"] = discord_manager.db_manager.get_last_gif_preference(select_person)

    assert (result == output)
