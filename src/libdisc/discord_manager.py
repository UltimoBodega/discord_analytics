from datetime import datetime, timezone

import discord  # type: ignore
from discord import TextChannel  # type: ignore

from discord_analytics.analytics_engine import AnalyticsEngine
from libdisc.database_manager import DatabaseManager
from libdisc.dataclasses.discord_objects import DiscordUser
from libdisc.media_manager import MediaManager
from libdisc.plot_manager import PlotManager


class DiscordManager:
    """
    This class serves as the primary orchestrator for any data exported from
    discord server.
    """

    def __init__(self, db_manager: DatabaseManager,
                 analytics_engine: AnalyticsEngine,
                 media_manager: MediaManager,
                 plot_manager: PlotManager):
        # dict where key is channel id and value last fetched timestamp
        self.db_manager = db_manager
        self.analytics_engine = analytics_engine
        self.media_manager = media_manager
        self.plot_manager = plot_manager

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
                                 exclude_bot: bool = True) -> str:
        """
        Sends out the latest user and character count analytics.

        @param channel: The channel to analyze and send.
        @param exclude_bot: Weather or not to include bot statistics.
        @return: a Discord friendly character statistics string.
        """
        char_count_dict = (self.analytics_engine.get_user_by_char_count(channel.id))
        output_str = '```'
        for user, count in sorted(char_count_dict.items(), key=lambda item: item[1], reverse=True):
            if exclude_bot and 'bot' in user:
                continue
            output_str += f"El {user}: {count}" + '\n'

        output_str += '```'
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
        filename = self.plot_manager.generate_trend_image(stats_item)
        return filename
