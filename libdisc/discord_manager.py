from datetime import datetime, timezone
from discord import TextChannel

from discord_analytics.analytics_engine import AnalyticsEngine
from libdisc.database_manager import DatabaseManager


class DiscordManager:
    """
    This class serves as the primary orchestrator for any data exported from discord server.
    """

    def __init__(self, db_manager: DatabaseManager, analytics_engine: AnalyticsEngine):
        # dict where key is channel id and value last fetched timestamp
        self.db_manager = db_manager
        self.analytics_engine = analytics_engine

    async def store_latest_chat_messages(self, channel: TextChannel) -> None:
        """
        Attempts to load chat messages since the last timestamp in the database.
        @param channel: The discord text channel.
        """
        last_timestamp = self.db_manager.get_last_message_timestamp(channel.id)
        after = datetime.utcfromtimestamp(last_timestamp) if last_timestamp else None
        messages_processed = 0
        async for msg in channel.history(limit=None, after=after):
            self.db_manager.add_new_message(user_name=msg.author.display_name,
                                            timestamp=int(msg.created_at.replace(tzinfo=timezone.utc).timestamp()),
                                            message_channel_id=channel.id,
                                            message_word_count=len(msg.content.split()),
                                            message_char_count=len(msg.content))
            messages_processed += 1
            if messages_processed % 100 == 0:
                print(messages_processed)

    def send_character_analytics(self, channel: TextChannel, exclude_bot: bool = True) -> str:
        """
        Sends out the latest user and character count analytics.
        @param channel: The channel to analyze and send.
        @param exclude_bot: Weather or not to include bot statistics.
        @return: a Discord friendly character statistics string.
        """
        char_count_dict = self.analytics_engine.get_user_by_char_count(channel.id)
        output_str = '```'
        for user, count in sorted(char_count_dict.items(), key=lambda item: item[1], reverse=True):
            if exclude_bot and 'bot' in user:
                continue
            output_str += f"El {user}: {count}" + '\n'

        output_str += '```'
        return output_str
