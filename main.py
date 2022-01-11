import os

import discord
from dotenv import load_dotenv

DIR_PATH = "/data/projets/genshinImage/bot/"

load_dotenv()


client = discord.Client()

@client.event
async def on_ready():
	print(f'currently logged as {client.user}')



@client.event
async def on_message(m):
	if m.author == client.user:
		return
	
	if m.content.startswith('$hello'):
		await m.channel.send('Hi !')


client.run(os.environ['TOKEN'])


