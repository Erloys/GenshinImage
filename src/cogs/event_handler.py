from datetime import datetime
from io import BytesIO
import logging

import discord
from discord.ext import commands

import image_handler
import constants
import BotInteraction
import utils



class Event(commands.Cog):

    def __init__(self, client: discord.Bot, logger: logging.Logger, database: image_handler.ImgHandler) -> None:
        self.client = client
        self.logger = logger
        self.database = database
    

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info(f"currently logged as {self.client.user}")
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        roles = [
        member.guild.get_role(constants.roles.DECO_CHANNEL) ,
        member.guild.get_role(constants.roles.DECO_MEMBER) ,
        member.guild.get_role(constants.roles.SAFE) ,
        member.guild.get_role(constants.roles.VISITOR)
        ]
        await member.add_roles(*roles)

        dm = await member.create_dm()
        fb = BotInteraction.Rapport(member.guild)

        await fb.process(dm.send, "bienvenue sur le serveur Genshin Image", delete_after=None)
    
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if not message.channel or isinstance(message.channel, discord.DMChannel):
            return
        
        elif message.id in self.client.last_message_delete:
            return
        
        elif not utils.isImgChan(message.channel.name):
            return
        
        time = datetime.utcnow()

        async for entry in message.guild.audit_logs(limit=1, action=discord.AuditLogAction.message_delete):
            log = entry
        
        isLogged = abs(log.created_at.time().second - time.time().second) < 1

        deleted_by = log.user.display_name if isLogged else message.author.display_name

        img = BytesIO()

        #delete database
        await message.attachments[0].save(img)
        archive_chan = message.guild.get_channel(constants.ARCHIVE)

        image = await archive_chan.send(file=discord.File(img, filename='backup.png'))

        text = f"message supprimer par {deleted_by} dans {message.channel.name}"

        fb = BotInteraction.Rapport(message.guild)
        fb.set_author(message.author.display_name, message.author.avatar.url)
        fb.set_img(image.attachments[0].url)
        fb.set_url(image.jump_url)

        await fb.process(fb.chan.send, text, delete_after=None)

    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        is_dm_chan = not message.channel or isinstance(message.channel, discord.DMChannel)
        not_server = is_dm_chan or message.guild.id != constants.SERVEUR_ID
        not_img = is_dm_chan or not message.attachments
        not_img_chan = is_dm_chan or not utils.isImgChan(message.channel.name)

        if is_dm_chan or not_server or not_img or not_img_chan:
            return
        
        elif utils.isUrl(message.content):
            #remplacer url par upload
            await utils.delete(self.client, message)
        
        elif len(message.attachments) > 1:
            for file in message.attachments:
                if 'image' not in file.content_type:
                    continue
                img = BytesIO()
                await file.save(img)
                await message.channel.send(file=discord.File(img, 'image.png'))
            
            await utils.delete(self.client, message)