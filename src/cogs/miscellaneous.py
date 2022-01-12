import logging

import discord
from discord.commands.context import ApplicationContext
from discord.ext import commands
from discord.commands import Option

import constants
import BotInteraction

class Miscellaneous(commands.Cog):
    def __init__(self, c: discord.Bot, l: logging.Logger) -> None:
        self.client = c
        self.logger = l
    

    @commands.slash_command(name='access', guild_ids=[constants.SERVEUR_ID])
    async def access(self,
    ctx: ApplicationContext,
    type: Option(str, description="type à configurer", choices=[constants.CH_TYPE.HOT, constants.CH_TYPE.NSFW]),
    state: Option(str, description="état de l'accès", choices=['Activer', 'Desactiver'])
    ):
        states = state == 'Activer'
        role = constants.CH_TO_ROLE[type]
        role = ctx.guild.get_role(role)

        if states:
            await ctx.author.add_roles(role)
        else:
            await ctx.author.remove_roles(role)

        fb = BotInteraction.Rapport(ctx.guild)
        await fb.process(ctx.respond, f'vos accès channels ont bien été mis à jour\n {role.mention} -> {state}', ephemeral=True)
