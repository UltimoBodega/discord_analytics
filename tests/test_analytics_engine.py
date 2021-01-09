import context
import pytest

from db.db import DB
from discord_analytics.analytics_engine import AnalyticsEngine
from libdisc.plot_manager import PlotManager

@pytest.mark.parametrize ("dbpath,channel_id,output",
[

#TC01.0: Simple success for char count
('sqlite:///'+context.curr_path+'/tests/support/bodega_discord.db', 790004680604123168, "{'Brikta': 97, 'Demmy': 80, 'Digital': 67, 'bodega-bot': 1110, 'bodega-test-bot': 38, 'ulix': 67}"),

#TC02.0: Fetching data for dummy channel ID
('sqlite:///'+context.curr_path+'/tests/support/bodega_discord.db', 0, "{}"),

#TC03.0: Fetching data for non integer channel ID
('sqlite:///'+context.curr_path+'/tests/support/bodega_discord.db', "dummy_str", "{}"),

#TC04.0: Bad filepath+filename for db
('/bodega_discord.db', 790004680604123168, "Could not parse rfc1738 URL from string '/bodega_discord.db'"),

])

def test_db_analytics(dbpath,channel_id,output) -> None:
    try:
        DB.get_instance().setup_db(dbpath)
        analytics_engine = AnalyticsEngine()
        result = analytics_engine.get_user_by_char_count(channel_id)
    except Exception as error_msg:
        result = error_msg

    assert(str(result) == output)



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