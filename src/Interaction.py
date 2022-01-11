from collections import namedtuple

import discord
from discord.commands.commands import command

import constants

class IMGURL:
    FEEDBACK = "https://cdn.discordapp.com/attachments/352826445191577600/922424899656626226/unknown.png"
    CANCEL = "https://cdn.discordapp.com/attachments/352826445191577600/922441727262982234/2Q.png"
    ERROR = "https://cdn.discordapp.com/attachments/352826445191577600/922466474919067688/220550-full.png"
    ASK = "https://cdn.discordapp.com/attachments/352826445191577600/922470726710214716/unknown.png"

class TYPE:
    __gloType = namedtuple("FEEDBACK_TYPE", ["title", "color", "img"])

    CONFIRM = __gloType("❓ Confirmer", color=constants.colors.gold, img=IMGURL.ASK)

    SELECT = __gloType(
        "📌 Select Menu", color=constants.colors.dark_orange, img=IMGURL.ASK
    )

    CANCEL = __gloType(
        title="❌ Annuler", color=constants.colors.blue, img=IMGURL.CANCEL
    )

    ERROR = __gloType(
        title="⚠️ Erreur", color=constants.colors.dark_red, img=IMGURL.ERROR
    )

    RAPPORT = __gloType(
        title="🔔 Rapport", color=constants.colors.green, img=IMGURL.FEEDBACK
    )


modType = namedtuple("FEEDBACK_MODERATION", ["title", "color", "action"])

BAN = modType(title="🔨 BAN", color=constants.colors.red, action="À banni ")

KICK = modType(title="🚪 Kick", color=constants.colors.gold, action="À expulser ")

UNBAN = modType(
    title=" ⚖ UNBAN",
    color=constants.colors.blue,
    action="À révoquer le bannissement de ",
)

ROLE_UPDATE = modType(
    title="⚙ UPDATE ROLE",
    action="À Mise a jour les roles de ",
    color=constants.colors.dark_green,
)

class Message:
    """sert de super classe"""

    chan = constants.LOGCHAN

    def __init__(self, type) -> None:
        self.type = type

        self.embed = self.makeEmbed()
    
    def makeEmbed(self):
        embed = discord.Embed(
            title = self.type.title,
            color=self.type.color
        )
        embed.set_thumbnail(url=self.type.img)

        return embed
    
    @property
    def fields(self):
        return self.embed.fields
    
    @fields.setter
    def field(self, a):
        self.embed.fields = a
    
    def set_img(self, img):
        self.embed.set_image(url=img)

    def set_author(self, name, img):
        self.author = name
        self.embed.set_author(name=name, icon_url=img)

    def set_url(self, url):
        self.embed.url = url

    def add_field(self, name: str, value: str, inline: bool):
        self.embed.add_field(name=name, value=value, inline=inline)

    def clone_fields(self, a):
        self.fields = a.fields
    

    async def process(self,send, message:str, files=None, delete_after=constants.TIMER):
        
        self.embed.description = message
        return await send(embed=self.embed, delete_after=delete_after, files=files)


class Rapport(Message):
    """envois un Rapport de commande"""

    def __init__(self, guild) -> None:
        super().__init__(TYPE.RAPPORT)

        self.chan = guild.get_channel(self.chan)
    

    async def process(self, send, message: str, files=None, delete_after=constants.TIMER, logger= None, logchan= None):
        if logger:
            logger.info(message)
        if logchan:
            await self.chan.send(embed=self.embed)
        return await super().process(send, message, files=files, delete_after=delete_after)


class Error(Message):
    def __init__(self, ctx, error, logger) -> None:
        super().__init__(TYPE.ERROR)
    
        self.ctx = ctx
        self.error = error
        self.logger = logger
    
    async def process(self, send, message: str, files=None, delete_after=constants.TIMER):
        
        self.logger.info(f"la commande {self.ctx.command} lancer par {self.ctx.author.display_name}"
        f"à provoquer l'erreur {self.error}")
        return await super().process(send, message, files=files, delete_after=delete_after)


class Cancel(Message):
    def __init__(self) -> None:
        super().__init__(TYPE.CANCEL)


class Moderation(Message):

    def __init__(self, type, ctx, logger) -> None:
        super().__init__(type)
        
        self.chan = ctx.guild.get_channel(self.chan)
        self.logger = logger
        self.ctx = ctx

        self.set_author(ctx.author.display_name, ctx.author.avatar_url)
    

    def makeEmbed(self):
        return discord.Embed(title=self.type.title, color=self.type.color)
    

    async def process(self, target: discord.User, reason: str, delete_after=constants.TIMER):
        message = self.type.action + target.display_name
        reason = 'raison : ' + reason

        self.logger.info(f"{self.type.title}: {self.author} - {message} - {reason}")
        self.embed.set_thumbnail(url=target.avatar_url)
        self.embed.add_field(name=message, value=reason, inline=False)

        await self.chan.send(embed=self.embed)

        return await self.ctx.send(embed=self.embed, delete_after=delete_after)


class AskButton(Message):
    def __init__(self, view) -> None:
        super().__init__(TYPE.CONFIRM)
        self.view = view
    

    async def process(self,send, message:str, files=None, delete_after=constants.TIMER):
        
        self.embed.description = message
        return await send(embed=self.embed, view=self.view, delete_after=delete_after, files=files)


class AskSelect(Message):
    def __init__(self) -> None:
        super().__init__(TYPE.SELECT)
    
    async def process(self,send, message:str, files=None, delete_after=constants.TIMER):
        
        self.embed.description = message
        return await send(embed=self.embed, view=self.view, delete_after=delete_after, files=files)
