import random
from datetime import datetime, timezone
from discord.ext import commands

from app_configs.config_manager import ConfigManager
from discord_analytics.analytics_engine import AnalyticsEngine
from libdisc.database_manager import DatabaseManager
from libdisc.discord_manager import DiscordManager
from libdisc.media_manager import MediaManager

def bodega_bot () -> None:
    """
    Main discord application entry point
    """
    client = commands.Bot(command_prefix='.')

    analytics_engine = AnalyticsEngine()
    database_manager = DatabaseManager()
    media_manager = MediaManager(ConfigManager.get_instance().get_giphy_api_key())
    discord_manager = DiscordManager(db_manager=database_manager, analytics_engine=analytics_engine,
                                     media_manager=media_manager)

    @client.event
    async def on_ready():
        print('Loading caches . . . .')
        database_manager.load_cache()
        print('Ready set go!')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        author = message.author.name
        utc_time = int(message.created_at.replace(tzinfo=timezone.utc).timestamp())

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

        if not str(message.content).startswith('.'):
            gif_url = discord_manager.handle_gif_cooldown(user_name=author, message_ts=utc_time)
            if gif_url:
                await message.channel.send(gif_url)

        groserias = ["joto", "puto", "maricon"]

        responses = ["Usaste un termino derrogativo en contra de nuestros amigxs homosexuales",
                    f"Not chill {author}, that's homophobic",
                    "Oye, que feo eres :/ ser homosexual no es malo",
                    f"¿Quién te crees {author}? ¿Molotov?",
                    f"{author}, you are willfully ignoring the virulently homophobic undertones of your statement."]

        if any(groseria in str(message.content).lower() for groseria in groserias):
            await message.channel.send(f"{random.choice(responses)}")

    client.run(ConfigManager.get_instance().get_bot_token())
