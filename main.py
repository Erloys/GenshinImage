import os

import discord
from dotenv import load_dotenv

import src.logger
import src.cogs as cogs

load_dotenv()

client = discord.Bot()

logger = src.logger.Make()


@client.event
async def on_ready():
	print(f'currently logged as {client.user}')


client.add_cog(cogs.Error(client, logger))
client.run(os.environ['TOKEN'])