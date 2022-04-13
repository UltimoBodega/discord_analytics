from datetime import datetime, timezone

import discord  # type: ignore
from discord import TextChannel  # type: ignore

from discord_analytics.analytics_engine import AnalyticsEngine
from libdisc.constants import SECONDS_IN_HOUR
from libdisc.database_manager import DatabaseManager
from libdisc.dataclasses.discord_objects import DiscordUser
from libdisc.media_manager import MediaManager
from libdisc.plot_manager import PlotManager
from libdisc.finance_manager import FinanceManager

from typing import List


class DiscordManager:
    """
    This class serves as the primary orchestrator for any data exported from
    discord server.
    """

    def __init__(self, db_manager: DatabaseManager,
                 analytics_engine: AnalyticsEngine,
                 media_manager: MediaManager,
                 plot_manager: PlotManager,
                 finance_manager: FinanceManager):
        # dict where key is channel id and value last fetched timestamp
        self.db_manager = db_manager
        self.analytics_engine = analytics_engine
        self.media_manager = media_manager
        self.plot_manager = plot_manager
        self.finance_manager = finance_manager

    async def store_latest_chat_messages(self,
                                         channel: TextChannel,
                                         is_backfill: bool = False) -> None:
        """
        Attempts to load chat messages since the last timestamp
        in the database.
        @param channel: The discord text channel.
        @param is_backfill: Whether or not backfill from beginning of time.
        """
        last_timestamp = self.db_manager.get_last_message_timestamp(channel.id)
        after = (datetime.utcfromtimestamp(last_timestamp) if last_timestamp else None)

        if is_backfill:
            after = None
            self.db_manager.reset_cache()

        messages_processed = 0
        async for msg in channel.history(limit=None, after=after):

            self.db_manager.add_new_message(
                discord_user=DiscordUser(msg.author.name,
                                         msg.author.display_name,
                                         msg.author.discriminator),
                timestamp=int(msg.created_at.replace(
                              tzinfo=timezone.utc).timestamp()),
                message_channel_id=channel.id,
                message_word_count=len(msg.content.split()),
                message_char_count=len(msg.content))
            messages_processed += 1
            if messages_processed % 100 == 0:
                print(messages_processed)

    def send_character_analytics(self,
                                 channel: TextChannel,
                                 exclude_bot: bool = True,
                                 hours_ago: int = 0) -> str:
        """
        Sends out the latest user and character count analytics.

        @param channel: The channel to analyze and send.
        @param exclude_bot: Weather or not to include bot statistics.
        @param hours_ago: Only count from starting hours_ago.
        @return: a Discord friendly character statistics string.
        """
        from_timestamp = int(datetime.now(timezone.utc).timestamp()) - hours_ago * SECONDS_IN_HOUR if hours_ago else 0
        char_count_dict = (self.analytics_engine.get_user_by_char_count(channel.id, from_timestamp))

        output_str = '```'
        if hours_ago:
            output_str += f'Message for the last {hours_ago} hours: \n'
            output_str += '----------------------------------------\n'
        for user, count in sorted(char_count_dict.items(), key=lambda item: item[1], reverse=True):
            if exclude_bot and 'bot' in user:
                continue
            output_str += f"El {user}: {count}" + '\n'

        output_str += '```'

        if output_str == '``````':
            return f'`No messages found in the last {hours_ago} hours`'

        return output_str

    def handle_gif_cooldown(self,
                            author: discord.User,
                            message_ts: int) -> str:
        """
        Handles whether or not the bot should post a Gif to
        the discord Channel.

        @param author: A Discord User
        @param message_ts: Timestamp of the latest message sent by user.
        @return: a Gif url string.
        """
        gif_url = ""
        discord_user = DiscordUser(author.name,
                                   author.display_name,
                                   author.discriminator)
        (keyword, gif_timestamp) = self.db_manager.get_last_gif_preference(discord_user)

        if keyword:
            if message_ts - gif_timestamp >= 60 * 60 * 24 * 3:  # 3 days
                gif_url = self.media_manager.get_gif(keyword)
            self.db_manager.upsert_new_gif_entry(
                discord_user=discord_user,
                keyword=keyword,
                timestamp=message_ts)

        return gif_url

    def get_random_gif(self, keyword: str) -> str:
        """
        Gets a random gif url from media manager

        @param keyword: keyword used to query gif repository
        @return: A random gif url associated with the keyword if found else a message saying it wasn't found.
        """
        return self.media_manager.get_gif(keyword) or f"No gifs found for keyword: {keyword}"

    def upsert_gif_keyword(self, author: discord.User, keyword: str) -> None:
        """
        Inserts a Gif keyword preference for a particular user.

        @param author: A Discord User
        @param keyword: Keyword used to find a gif.
        @return: None
        """
        self.db_manager.upsert_new_gif_entry(discord_user=DiscordUser(author.name,
                                                                      author.display_name,
                                                                      author.discriminator),
                                             keyword=keyword)

    def handle_trend_command(self,
                             channel: TextChannel, message_ts: int,
                             week_limit: int = 30) -> str:
        """
        Creates a trend plot displaying user's char weekly statistics.

        @param channel: A Discord's channel object
        @param message_ts: Timestamp of the latest message sent.
        @param week_limit: Number of weeks to show in trend relative to
        current time.
        @return: Filename of the trend image (png) file
        """
        sec_in_week = 60 * 60 * 24 * 7
        limit_ts = (int(message_ts / sec_in_week) - week_limit) * sec_in_week
        stats_item = self.analytics_engine.get_stats_grouped_by_time(channel.id, limit_ts)
        filename = self.plot_manager.generate_trend_image(
            chart_title='User Trends',
            x_label='Time',
            y_label='Char count',
            stat_item=stats_item)
        return filename

    def handle_stock_trend_command(self,
                                   symbols: List[str],
                                   day_limit: int) -> str:
        """
        Prints stock trends for each symbol
        :param symbols: _description_
        :return: _description_
        """
        query_symbols: List[str] = []
        existing_symbols = set(self.db_manager.get_all_tracking_symbols())
        if len(symbols) == 0:
            query_symbols.extend(existing_symbols)
        else:
            query_symbols.extend(
                (sym for sym in symbols if sym in existing_symbols))

        sec_in_day = 60 * 60 * 24
        from_ts = datetime.now(timezone.utc).timestamp() - sec_in_day * day_limit
        stats_item = self.db_manager.get_stock_history(symbols=query_symbols,
                                                       from_ts=from_ts)
        if len(query_symbols) == 0:
            return ''

        filename = self.plot_manager.generate_trend_image(
            chart_title='Stock Trends',
            x_label='Date',
            y_label='$',
            stat_item=stats_item)
        return filename

    def handle_stock_command(self, symbol: str) -> str:
        """
        Returns current stock price
        @param symbol: the stock symbol
        @return: message containing current stock price
        """
        special_symbols = {
            'FAANG': ['FB', 'AMZN', 'AAPL', 'NFLX', 'GOOG']
        }
        msg = ""
        if symbol in special_symbols:
            msg = f':rocket::rocket::rocket:{symbol}:rocket::rocket::rocket:\n'
            msg += '```'
            stock_dict = self.finance_manager.get_stock_item_concurrent(special_symbols[symbol])
            for sym in special_symbols[symbol]:
                msg += f'{sym}: ${stock_dict[sym].price}\n'
            msg += '```'
        else:
            msg += '```'
            msg += f'{symbol}: ${self.finance_manager.get_stock_item(symbol).price}'
            msg += '```'
        return msg

    def handle_track_command(self, symbol: str) -> str:
        item = self.finance_manager.get_stock_item(symbol)
        valid = self.finance_manager.check_valid_stock(item)
        if not valid:
            return f'{symbol} is not a valid symbol.'
        self.db_manager.add_stock_track(symbol)
        return f'Now tracking {symbol}'

    def handle_add_alert_command(self,
                                 author: discord.User,
                                 channel: TextChannel,
                                 low: int,
                                 high: int,
                                 symbol: str,
                                 note: str) -> str:
        """
        Adds a stock alert, if symbol is not being tracked it will attempt to track it
        :param author: _description_
        :param channel: _description_
        :param low: _description_
        :param high: _description_
        :param symbol: _description_
        :param note: _description_
        :return: _description_
        """
        print(f'Adding alert {symbol}: {low} {high}')
        symbols = set(self.db_manager.get_all_tracking_symbols())
        if symbol not in symbols:
            valid = self.finance_manager.check_valid_stock(
                self.finance_manager.get_stock_item(symbol))
            if not valid:
                return f'Alert wasnt added, {symbol} is not a valid symbol.'
            self.db_manager.add_stock_track(symbol)
        self.db_manager.add_stock_alert(
            discord_user=DiscordUser(author.name,
                                     author.display_name,
                                     author.discriminator),
            timestamp=datetime.now(timezone.utc).timestamp(),
            channel_id=channel.id,
            symbol=symbol,
            low=low,
            high=high,
            note=note)
        return f'Alert from {author.display_name} for {symbol} added!'
