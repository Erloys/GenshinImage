import os

import discord
from dotenv import load_dotenv

import src.logger
import src.cogs as cogs
import src.image_handler

load_dotenv()

intents = discord.Intents().all()
client = discord.Bot(intents=intents)

client.last_message_delete = []
logger = src.logger.Make()

database = src.image_handler.ImgHandler('/data/projets/discord/database/GenshinImage', logger)

client.add_cog(cogs.Misc(client, logger, database))
client.add_cog(cogs.Admin(client, logger))
client.add_cog(cogs.Mod(client, database, logger))
client.add_cog(cogs.Event(client, logger, database))
client.add_cog(cogs.Error(client, logger))
client.run(os.environ['TOKEN'])