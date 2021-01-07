import random
from datetime import datetime, timezone
from discord.ext import commands
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app_configs.config_manager import ConfigManager
from discord_analytics.analytics_engine import AnalyticsEngine
from libdisc.database_manager import DatabaseManager
from libdisc.discord_manager import DiscordManager
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
    discord_manager = DiscordManager(db_manager=database_manager, analytics_engine=analytics_engine)

    @client.event
    async def on_ready():
        print('Fierro pariente! :)')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        if str(message.content).startswith('.stats'):
            await message.channel.send(f"Fetching character count by user......")
            await discord_manager.store_latest_chat_messages(channel=message.channel)
            await message.channel.send(discord_manager.send_character_analytics(message.channel))

        if str(message.content).startswith('.backfill'):
            await message.channel.send(f"Forcing message backfill insertion this might take a while")
            await discord_manager.store_latest_chat_messages(channel=message.channel, is_backfill=True)
            await message.channel.send(f"Backfill complete!")

        if str(message.content).startswith('.debug'):
            utc_time = int(message.created_at.replace(tzinfo=timezone.utc).timestamp())
            print(message.created_at)
            print(datetime.utcnow())
            print(datetime.utcfromtimestamp(utc_time))

        groserias = ["joto", "puto", "maricon"]
        author = message.author.display_name
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