import logging
import sys
import asyncio
import traceback

from discord.errors import Forbidden

sys.path.append('/data/projets/genshinImage/bot/src/')
import discord
from discord.ext import commands

import Interaction
import constants


class Error(commands.Cog):
	def __init__(self, client: discord.Bot, logger: logging.Logger):
		self.client = client
		self.logger = logger
	
	@commands.slash_command(name='test')
	async def test(self, ctx):
		await ctx.respond('fait')
		raise Exception

	@commands.Cog.listener()
	async def on_application_command_error(self, ctx: commands.Context, error):
		print(f"la commands {ctx.command.name} à provoquer l'erreur {error}")

		fb = Interaction.Error(ctx, error, self.logger)

		# commande annuler

		if isinstance(error, constants.CancelError):
			message = str(error)
			fb = Interaction.Cancel()
		
		elif isinstance(error, asyncio.TimeoutError):
			message = "⏱ TEMPS ÉCOULER"
			fb = Interaction.Cancel()

		elif isinstance(error, AttributeError):
			message = "il semblerai que cette commande rencontre des bugs dans \
			cette version"
			traceback.print_exception(
				type(error), error, error.__traceback__, file=sys.stderr)

		elif isinstance(error, Forbidden):
			message = "je ne possède pas les permissions necessaire \
			pour effectuer la commande"

		else:
			message = "je suis incapable de vous renseigner sur l'erreur"
			traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr
            )

		await fb.process(ctx.send, message)
