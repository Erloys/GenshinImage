import logging
import sys
import asyncio
import traceback
from discord.commands.commands import slash_command
from discord.commands.context import ApplicationContext

from discord.commands.errors import CheckFailure

from discord.errors import Forbidden

sys.path.append('/data/projets/genshinImage/bot/src/')
import discord
from discord.ext import commands

import BotInteraction
import constants


class Error(commands.Cog):
	def __init__(self, client: discord.Bot, logger: logging.Logger):
		self.client = client
		self.logger = logger
	

	@commands.Cog.listener()
	async def on_application_command_error(self, ctx: ApplicationContext, error):
		error = getattr(error, 'original', error)
		
		fb = BotInteraction.Error(ctx, error, self.logger)

		# commande annuler

		if isinstance(error, constants.CancelError):
			message = str(error)
			fb = BotInteraction.Cancel()

		# ERREUR
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

		await fb.process(ctx.respond, message)
