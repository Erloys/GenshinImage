import logging

import discord
from discord import utils
from discord.commands.context import ApplicationContext
from discord.ext import commands
from discord.commands import permissions

import constants
import utils
import BotInteraction

def check(m):
    return utils.isOwner(m.author, m.guild)

class Administration(commands.Cog):

    def __init__(self, client: discord.Bot, logger: logging.Logger) -> None:
        self.client = client
        self.logger = logger
    
    @commands.slash_command(name='owner', guild_ids=[constants.SERVEUR_ID])
    @permissions.is_owner()
    @permissions.is_user(constants.OWNER_ID)
    async def owner(self, ctx: ApplicationContext):
        """bascule entre le mode normal et le mode Owner"""
        role = ctx.guild.get_role(constants.roles.OWNER)

        
        if role in ctx.author.roles:
            text = 'owner mode activate'
            await ctx.author.remove_roles(role)
        else:
            text = 'owner mode disable'
            await ctx.author.add_roles(role)
        
        fb = BotInteraction.Rapport(ctx.guild)
        
        await fb.process(ctx.respond, text, ephemeral=True)