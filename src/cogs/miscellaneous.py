from io import BytesIO
import logging
import random

import discord
from discord import utils
from discord.commands.context import ApplicationContext
from discord.ext import commands
from discord.commands import Option

import constants
import BotInteraction
import utils
import image_handler as imgh

class Miscellaneous(commands.Cog):
    def __init__(self, c: discord.Bot, l: logging.Logger, d: imgh.ImgHandler) -> None:
        self.client = c
        self.logger = l
        self.database = d
    

    @commands.slash_command(name='access', guild_ids=[constants.SERVEUR_ID])
    async def access(self,
    ctx: ApplicationContext,
    type: Option(str, description="type à configurer", choices=[constants.channelsType.HOT, constants.channelsType.NSFW]),
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

    @commands.slash_command(name='rand', guild_ids=[constants.SERVEUR_ID])
    async def rand(self,
    ctx: ApplicationContext,
    name: Option(str, description='nom du personnage', required=False) = None,
    tag: Option(str, description="type d'image", required=False, choices=[constants.channelsType.SAFE, constants.channelsType.HOT, constants.channelsType.NSFW]) = constants.channelsType.SAFE
    ):
        if name is None:
            name = tag
        is_dm_chan = ctx.channel is None or isinstance(ctx.channel, discord.DMChannel)
        is_command_chan = not is_dm_chan and ctx.channel.name == "🤖・commandes-bots"
        is_nsfw = not is_dm_chan and ctx.channel.nsfw

        if not (is_dm_chan or is_command_chan or utils.isOwner(ctx.author, ctx.guild) ):
            raise constants.CancelError("la commande rand est désactiver dans ce canal")
        
        ephemeral = not is_dm_chan and tag == constants.channelsType.NSFW and not is_nsfw
        spoiler = tag in [constants.channelsType.HOT, constants.channelsType.NSFW] and not is_nsfw

        liste = self.database.get_index()

        liste = [i for i in liste if (name in i.tag and tag in i.tag)]

        if not liste:
            raise constants.CancelError("Oups aucune image ne coresponds à ces critères")

        img = self.database.get_image(imgh.id_to_path(random.choice(liste).id))

        await ctx.send_response(file=discord.File(BytesIO(img), filename="image.png", spoiler=spoiler), ephemeral=ephemeral)