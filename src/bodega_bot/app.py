import random
import threading
from datetime import datetime, timezone
from typing import Callable, Any, List

import discord  # type: ignore
from discord.ext import commands  # type: ignore
from discord_slash import SlashCommand, SlashContext, SlashCommandOptionType  # type: ignore
from discord_slash.utils.manage_commands import create_option  # type: ignore

from app_configs.config_manager import ConfigManager
from discord_analytics.analytics_engine import AnalyticsEngine
from libdisc.database_manager import DatabaseManager
from libdisc.discord_manager import DiscordManager
from libdisc.finance_manager import FinanceManager
from libdisc.media_manager import MediaManager
from libdisc.plot_manager import PlotManager
from libdisc.dataclasses.discord_objects import StockItem, AlertItem


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
    finance_manager = FinanceManager()
    discord_manager = DiscordManager(
        db_manager=database_manager,
        analytics_engine=analytics_engine,
        media_manager=media_manager,
        plot_manager=plot_manager,
        finance_manager=finance_manager)

    @client.event
    async def on_ready():
        print('Loading caches . . . .')
        database_manager.load_cache()
        print('Starting Firestore . . . .')
        database_manager.start_fs()
        database_manager.init_history_watch(_alerting)
        print('Ready set go!')

    def _alerting(stock_item: StockItem, alert_item: AlertItem) -> bool:
        msg = 'invalid alert'
        if alert_item.low > stock_item.price:
            msg = (f'Alert! Symbol: {alert_item.symbol}: {stock_item.price} '
                   f'became lower than: {alert_item.low}, {alert_item.note}')
        elif alert_item.high < stock_item.price:
            msg = (f'Alert! Symbol: {alert_item.symbol}: {stock_item.price} '
                   f'became higher than: {alert_item.high}, {alert_item.note}')
        client.loop.create_task(
            client.get_channel(alert_item.channel_id).send(msg))
        return True

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

    @slash.slash(
        name="stocktrend",
        description="Shows stock trend of tracked stocks.",
        guild_ids=ConfigManager.get_instance().get_guild_ids(),
        options=[
            create_option(
                name="stocks_and_limit",
                description=("Comma seperated list "
                             "optionally with day limit in the end. eg. "
                             "MSFT,GOOG,30"),
                required=False,
                option_type=SlashCommandOptionType.STRING
            )
        ]
    )
    async def _stocktrend(ctx: SlashContext, stocks_and_limit: str = ''):
        symbols: List[str] = []
        day_limit = 5
        if len(stocks_and_limit):
            params = str.split(stocks_and_limit, ',')
            if params[- 1].strip().isnumeric():
                day_limit = int(params[-1].strip())
                params = params[:-1]
            symbols.extend(param.strip() for param in params)
        if len(symbols) > 4:
            await ctx.send('Too many symbols, keep it under 4. Querying trend is expensive!')
            return
        if day_limit > 30:
            await ctx.send('Please keep day limit under 5, Querying trend is expensive!')
            return
  
        await ctx.defer()
        filename = discord_manager.handle_stock_trend_command(
            symbols=symbols,
            day_limit=day_limit)
        if filename:
            await ctx.send(file=discord.File(filename))
        else:
            await ctx.send('No valid tracking symbols found')

    @slash.slash(
        name="stock",
        description="Fetches the price of stock symbol",
        guild_ids=ConfigManager.get_instance().get_guild_ids(),
        options=[
            create_option(
                name="symbol",
                description="stock symbol",
                required=True,
                option_type=SlashCommandOptionType.STRING
            )
        ]
    )
    async def _stock(ctx: SlashContext, symbol: str):
        await ctx.send(f'scheduling {symbol} look up!')
        _unblocking_call(ctx=ctx,
                         handler=discord_manager.handle_stock_command,
                         symbol=symbol)

    @slash.slash(
        name="track",
        description="Tracks a stock symbol",
        guild_ids=ConfigManager.get_instance().get_guild_ids(),
        options=[
            create_option(
                name="symbol",
                description="stock symbol",
                required=True,
                option_type=SlashCommandOptionType.STRING
            )
        ]
    )
    async def _track(ctx: SlashContext, symbol: str):
        await ctx.send(f'Tracking {symbol}!')
        _unblocking_call(ctx=ctx,
                         handler=discord_manager.handle_track_command,
                         symbol=symbol)

    @slash.slash(
        name="showtracked",
        description="Shows tracked symbols",
        guild_ids=ConfigManager.get_instance().get_guild_ids(),
    )
    async def _show_tracked(ctx: SlashContext):
        await ctx.send(discord_manager.handle_show_tracked_command())

    @slash.slash(
        name="addalert",
        description="Adds an alert for stock symbol",
        guild_ids=ConfigManager.get_instance().get_guild_ids(),
        options=[
            create_option(
                name="symbol_low_high_note",
                description="comma seperated list of: symbol,low trigger,high trigger,note",
                required=True,
                option_type=SlashCommandOptionType.STRING
            ),
        ]
    )
    async def _addalert(ctx: SlashContext, symbol_low_high_note: str):
        params = str.split(symbol_low_high_note, ',')
        if len(params) != 4:
            await ctx.send('Must supply parameter in form of symbol,low,high,note ' +
                           'eg. MSFT,200,400,remind me')
            return

        if not params[1].strip().isnumeric():
            await ctx.send('Second parameter must be a number')
            return
        if not params[2].strip().isnumeric():
            await ctx.send('Third parameter must be a number')
            return

        await ctx.send(f'Adding alert for {symbol_low_high_note}!')
        _unblocking_call(ctx=ctx,
                         handler=discord_manager.handle_add_alert_command,
                         author=ctx.author,
                         channel=ctx.channel,
                         symbol=params[0].strip(),
                         low=int(params[1].strip()),
                         high=int(params[2].strip()),
                         note=params[3].strip())

    def _unblocking_call(ctx: SlashContext,
                         handler: Callable[..., str],
                         **kwargs: Any):
        def send():
            client.loop.create_task(ctx.channel.send(handler(**kwargs)))

        _thread = threading.Thread(name='non-blocking', target=send)
        _thread.start()

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
