import discord_analytics.analytics_adapter as dan

disc_analytics = dan.Discord_Analytics()
disc_analytics.download_chat_messages()
disc_analytics.compute_chat_analytics()