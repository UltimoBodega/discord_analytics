import context
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from libdisc.models.base_mixin import Base
from discord_analytics.analytics_engine import AnalyticsEngine

@pytest.mark.parametrize ("dbpath,channel_id,output",
[

#TC01.0: Simple success for char count
('sqlite:///'+context.curr_path+'/tests/support/bodega_discord.db', 790004680604123168, "{'Brikta': 97, 'Demmy': 80, 'Digital': 67, 'bodega-bot': 1110, 'bodega-test-bot': 38, 'ulix': 67}"),

#TC02.0: Fetching data for dummy channel ID
('sqlite:///'+context.curr_path+'/tests/support/bodega_discord.db', 0, "{}"),

#TC03.0: Fetching data for dummy channel ID
('/bodega_discord.db', 790004680604123168, "Could not parse rfc1738 URL from string '/bodega_discord.db'"),

])

def test_db_analytics(dbpath,channel_id,output):
    result = None
    try:
        engine = create_engine(dbpath, pool_recycle=600)
        Base.metadata.create_all(engine)
        curr_session = sessionmaker(bind=engine)()
        analytics_engine = AnalyticsEngine(db_session=curr_session)
        result = analytics_engine.get_user_by_char_count(channel_id)
    except Exception as error_msg:
        result = error_msg

    assert(str(result) == output)