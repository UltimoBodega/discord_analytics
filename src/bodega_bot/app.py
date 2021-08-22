import random
from datetime import datetime, timezone

import discord  # type: ignore
from discord.ext import commands  # type: ignore
from discord_slash import SlashCommand, SlashContext  # type: ignore
from discord_slash.utils.manage_commands import create_option  # type: ignore

from app_configs.config_manager import ConfigManager
from discord_analytics.analytics_engine import AnalyticsEngine
from libdisc.database_manager import DatabaseManager
from libdisc.discord_manager import DiscordManager
from libdisc.media_manager import MediaManager
from libdisc.plot_manager import PlotManager


def bodega_bot() -> None:
    """
    Main discord application entry point
    """
    client = commands.Bot(command_prefix='.')
    slash = SlashCommand(client, sync_commands=True)

    analytics_engine = AnalyticsEngine()
    plot_manager = PlotManager()
    database_manager = DatabaseManager()
    media_manager = MediaManager(ConfigManager.get_instance().get_giphy_api_key())
    discord_manager = DiscordManager(
        db_manager=database_manager,
        analytics_engine=analytics_engine,
        media_manager=media_manager,
        plot_manager=plot_manager)

    @client.event
    async def on_ready():
        print('Loading caches . . . .')
        database_manager.load_cache()
        print('Ready set go!')

    @slash.slash(
        name="stats",
        description="Fetches the activity of the channel.",
        guild_ids=ConfigManager.get_instance().get_guild_ids(),
        options=[
            create_option(
                name="hours_ago",
                description="counts only from hours ago",
                required=False,
                option_type=4
            )
        ]
    )
    async def _stats(ctx: SlashContext, hours_ago: int = 0):
        await ctx.send("Backfilling stats...")
        await discord_manager.store_latest_chat_messages(channel=ctx.channel)
        await ctx.send(discord_manager.send_character_analytics(channel=ctx.channel, hours_ago=hours_ago))

    @slash.slash(
        name="trend",
        description="Shows trend of the channel's activity.",
        guild_ids=ConfigManager.get_instance().get_guild_ids(),
        options=[
            create_option(
                name="week_limit",
                description="Choose week limit.",
                required=False,
                option_type=4
            )
        ]
    )
    async def _trend(ctx: SlashContext, week_limit: int = 30):
        utc_time = int(ctx.created_at.replace(tzinfo=timezone.utc).timestamp())
        await ctx.send("Backfilling stats...")
        await discord_manager.store_latest_chat_messages(channel=ctx.channel)
        filename = discord_manager.handle_trend_command(
            channel=ctx.channel,
            message_ts=utc_time,
            week_limit=week_limit)
        await ctx.send(file=discord.File(filename))

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        author = message.author
        utc_time = int(message.created_at.replace(tzinfo=timezone.utc).timestamp())

        if str(message.content).startswith('.keyword'):
            latest_message = message.content.split(" ")
            keyword = " ".join(latest_message[1: len(latest_message)])
            discord_manager.upsert_gif_keyword(author, keyword)
            await message.channel.send(f"Upserted keyword: {keyword}")

        if str(message.content).startswith('.backfill'):
            await message.channel.send("Forcing message backfill insertion this might take a while")
            await discord_manager.store_latest_chat_messages(channel=message.channel, is_backfill=True)
            await message.channel.send("Backfill complete!")

        if str(message.content).startswith('.gif'):
            latest_message = message.content.split(" ")
            keyword = " ".join(latest_message[1: len(latest_message)])
            await message.channel.send(discord_manager.get_random_gif(keyword))

        if str(message.content).startswith('.debug'):
            print(message.created_at)
            print(datetime.utcnow())
            print(datetime.utcfromtimestamp(utc_time))

        if not str(message.content).startswith('.'):
            gif_url = discord_manager.handle_gif_cooldown(author=author, message_ts=utc_time)
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
