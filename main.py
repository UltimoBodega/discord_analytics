import discord
import random
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

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    groserias = ["joto", "puto", "maricon"]
    author = str(message.author).split("#", 1)[0]
    responses = ["Usaste un termino derrogativo en contra de nuestros amigxs homosexuales",
                 f"Not chill {author}, that's homophobic",
                 "Oye, que feo eres :/ ser homosexual no es malo",
                 f"¿Quién te crees {author}? ¿Molotov?",
                 f"{author}, you are willfully ignoring the virulently homophobic undertones of your statement."]
    
    for groseria in groserias:
        if groseria in str(message.content).lower():
            await message.channel.send(f"{random.choice(responses)}")
            break

client.run(disc_analytics.bot_token)