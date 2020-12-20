import discord
from discord.ext import commands
import discord_analytics.analytics_adapter as dan

disc_analytics = dan.Discord_Analytics()

client = commands.Bot(command_prefix='.')

@client.event
async def on_ready():
    print('Fierro pariente! :)')

@client.command(aliases=['stats'])
async def _stats(ctx):
    await ctx.send(f"Voy a ocupar unos minutos, por mientras puedes ir por un cafeciiito, un paneciiito...")
    disc_analytics.download_chat_messages()
    output_str = disc_analytics.compute_chat_analytics()
    await ctx.send(output_str)

client.run(disc_analytics.bot_token)