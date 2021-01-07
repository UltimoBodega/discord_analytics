import random
from datetime import datetime, timezone
from discord.ext import commands
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app_configs.config_manager import ConfigManager
from discord_analytics.analytics_engine import AnalyticsEngine
from libdisc.database_manager import DatabaseManager
from libdisc.discord_manager import DiscordManager
from libdisc.media_manager import MediaManager
from libdisc.models.base_mixin import Base
from libdisc.models.base_mixin import BaseModel

def bodega_bot () -> None:
    """
    Main discord application entry point
    """
    client = commands.Bot(command_prefix='.')
    engine = create_engine(ConfigManager.get_instance().get_db_url(), pool_recycle=299, pool_pre_ping=True)
    BaseModel.metadata.create_all(engine)
    session_maker =  sessionmaker(bind=engine)
    curr_session = session_maker()
    analytics_engine = AnalyticsEngine(db_session=curr_session)
    database_manager = DatabaseManager(db_session=curr_session)
    media_manager = MediaManager(ConfigManager.get_instance().get_giphy_api_key())
    discord_manager = DiscordManager(db_manager=database_manager, analytics_engine=analytics_engine,
                                     media_manager=media_manager)
    

    @client.event
    async def on_ready():
        print('Fierro pariente! :)')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        author = message.author.display_name
        utc_time = int(message.created_at.replace(tzinfo=timezone.utc).timestamp())
        gif_url = discord_manager.handle_gif_cooldown(user_name=author, message_ts=utc_time)
        if gif_url:
            await message.channel.send(gif_url)

        if str(message.content).startswith('.stats'):
            await message.channel.send(f"Fetching character count by user......")
            await discord_manager.store_latest_chat_messages(channel=message.channel)
            await message.channel.send(discord_manager.send_character_analytics(message.channel))

        if str(message.content).startswith('.keyword'):
            latest_message = message.content.split(" ")
            keyword = " ".join(latest_message[1: len(latest_message)])
            discord_manager.upsert_gif_keyword(author, keyword)
            await message.channel.send(f"Upserted keyword: {keyword}")

        if str(message.content).startswith('.backfill'):
            await message.channel.send(f"Forcing message backfill insertion this might take a while")
            await discord_manager.store_latest_chat_messages(channel=message.channel, is_backfill=True)
            await message.channel.send(f"Backfill complete!")

        if str(message.content).startswith('.debug'):
            print(message.created_at)
            print(datetime.utcnow())
            print(datetime.utcfromtimestamp(utc_time))

        if str(message.content).lower().startswith('hola'):
            gif = media_manager.get_gif(map_dict[author])
            await message.channel.send(gif)

        groserias = ["joto", "puto", "maricon"]
        
        responses = ["Usaste un termino derrogativo en contra de nuestros amigxs homosexuales",
                    f"Not chill {author}, that's homophobic",
                    "Oye, que feo eres :/ ser homosexual no es malo",
                    f"¿Quién te crees {author}? ¿Molotov?",
                    f"{author}, you are willfully ignoring the virulently homophobic undertones of your statement."]
        
        for groseria in groserias:
            if groseria in str(message.content).lower():
                await message.channel.send(f"{random.choice(responses)}")
                break

    client.run(ConfigManager.get_instance().get_bot_token())