import random
import context
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.db import DB
from discord_analytics.analytics_engine import AnalyticsEngine
from libdisc.database_manager import DatabaseManager
from libdisc.discord_manager import DiscordManager
from libdisc.media_manager import MediaManager
from libdisc.models.base_mixin import BaseModel

def test_gif_db() -> None:
    """
    Tests the 'upsert' and 'get' method of the Gif class.

    Test procedure:
    1- Reads empty db.
    2- Inserts data to empty db using upsert.
    3- Reads db.
    4- Updates data to db using upsert.
    5- Reads updated db.
    """
    preferences = [("John", "Matrix", 150), ("Jane", "The Notebook", 150000),
            ("Bob", "Stranger Things", 0), ("Mike", "Iron Man", 10000)]
    result = {}
    select_person = "Bob"
    update_data = (select_person, "Twin Peaks", 75000)
    filename = "test_db_models.db"
    db_url = "sqlite:///"+filename
    gif_dummy_key = ""
    output = {'Read empty': ('', 0), 'Initial preference': ('Stranger Things', 0), 'Read update': ('Twin Peaks', 75000)}

    DB.get_instance().setup_db(db_url)
    analytics_engine = AnalyticsEngine()
    database_manager = DatabaseManager()
    media_manager = MediaManager(gif_dummy_key)
    discord_manager = DiscordManager(db_manager=database_manager, analytics_engine=analytics_engine,
                                    media_manager=media_manager)


    # Query empty DB for Bob - should return nothing
    result["Read empty"] = discord_manager.db_manager.get_last_gif_preference(select_person)
    # discord_manager.db_manager.upsert_new_gif_entry()

    for preference in preferences:
        (user_name, keyword, timestamp) = preference
        discord_manager.db_manager.upsert_new_gif_entry(user_name, keyword, timestamp)

    # Read for Bob - should initial preference
    result["Initial preference"] = discord_manager.db_manager.get_last_gif_preference(select_person)

    # Update Bob's preferences
    (user_name, keyword, timestamp) = update_data
    discord_manager.db_manager.upsert_new_gif_entry(user_name, keyword, timestamp)

    # Read for Bob - should initial preference
    result["Read update"] = discord_manager.db_manager.get_last_gif_preference(select_person)
    
    os.remove(filename)
    assert(result==output)