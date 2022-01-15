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
            text = 'owner mode disable'
            await ctx.author.remove_roles(role)
        else:
            text = 'owner mode activate'
            await ctx.author.add_roles(role)
        
        fb = BotInteraction.Rapport(ctx.guild)
        
        await fb.process(ctx.respond, text, ephemeral=True)
    
    @commands.slash_command(name='reperms', guild_ids=[constants.SERVEUR_ID])
    @permissions.is_owner()
    @permissions.is_user(constants.OWNER_ID)
    async def reperms(self, ctx: ApplicationContext):
        await ctx.defer()
        channels : list[discord.TextChannel] = ctx.guild.text_channels

        role = ctx.guild.get_role(constants.roles.EVERYONE)
        for c in channels:
            if not utils.isImgChan(c.name):
                continue
            await c.set_permissions(role, use_slash_commands=False)
        
        await ctx.send_followup("done", ephemeral=True)
    
    @commands.slash_command(name='scandb', guild_ids=[constants.SERVEUR_ID])
    @permissions.is_owner()
    @permissions.is_user(constants.SERVEUR_ID)
    async def scandb(self, ctx: ApplicationContext):
        channels: list[discord.TextChannel] = ctx.guild.channels

        for c in channels:
            if not utils.isImgChan(c.name):
                continue
            messages = await c.history(limit=25).flatten()
            for m in messages:
                self.client.dispatch('message', m)
    
    @commands.slash_command(name='fix_confirm', guild_ids=[constants.SERVEUR_ID])
    @permissions.is_user(constants.OWNER_ID)
    async def fix(self, ctx: ApplicationContext):
        c: discord.TextChannel = ctx.guild.get_channel(919487889719570432)
        logconfirm: discord.TextChannel = ctx.guild.get_channel(constants.channels.LOG_CONFIRM)
        messages = await c.history().flatten()

        for m in messages:
            if '@' not in m.embeds[0].footer.text:
                await logconfirm.send(embed=m.embeds[0])
                await m.delete()