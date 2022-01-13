from collections import namedtuple
from typing import Optional

import discord
from discord.embeds import EmptyEmbed
import discord.interactions
from discord.commands.commands import command

import constants
import utils

class IMGURL:
    FEEDBACK = "https://cdn.discordapp.com/attachments/352826445191577600/922424899656626226/unknown.png"
    CANCEL = "https://cdn.discordapp.com/attachments/352826445191577600/922441727262982234/2Q.png"
    ERROR = "https://cdn.discordapp.com/attachments/352826445191577600/922466474919067688/220550-full.png"
    ASK = "https://cdn.discordapp.com/attachments/352826445191577600/922470726710214716/unknown.png"

    NotFound ="https://cdn.discordapp.com/attachments/352826445191577600/930899285761990656/995lM6a.png"

class TYPE:
    __gloType = namedtuple("FEEDBACK_TYPE", ["title", "color", "img"])

    CONFIRM = __gloType("❓ Confirmer", color=constants.Colors.gold, img=IMGURL.ASK)

    SELECT = __gloType(
        "📌 Select Menu", color=constants.Colors.dark_orange, img=IMGURL.ASK
    )

    CANCEL = __gloType(
        title="❌ Annuler", color=constants.Colors.blue, img=IMGURL.CANCEL
    )

    ERROR = __gloType(
        title="⚠️ Erreur", color=constants.Colors.dark_red, img=IMGURL.ERROR
    )

    RAPPORT = __gloType(
        title="🔔 Rapport", color=constants.Colors.green, img=IMGURL.FEEDBACK
    )


modType = namedtuple("FEEDBACK_MODERATION", ["title", "color", "action"])

BAN = modType(title="🔨 BAN", color=constants.Colors.red, action="À banni ")

KICK = modType(title="🚪 Kick", color=constants.Colors.gold, action="À expulser ")

UNBAN = modType(
    title=" ⚖ UNBAN",
    color=constants.Colors.blue,
    action="À révoquer le bannissement de ",
)

ROLE_UPDATE = modType(
    title="⚙ UPDATE ROLE",
    action="À Mise a jour les roles de ",
    color=constants.Colors.dark_green,
)

class Message:
    """sert de super classe"""

    chan = constants.channels.LOGCHAN

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
    
    def set_footer(self, text, img=EmptyEmbed):
        self.embed.set_footer(text=text, icon_url=img)

    def set_author(self, name, img):
        self.author = name
        self.embed.set_author(name=name, icon_url=img)

    def set_url(self, url):
        self.embed.url = url

    def add_field(self, name: str, value: str, inline: bool):
        self.embed.add_field(name=name, value=value, inline=inline)

    def clone_fields(self, a):
        self.fields = a.fields
    

    async def process(self,send, message:str, delete_after=constants.TIMER, **kwargs):
        
        self.embed.description = message
        return await send(embed=self.embed, delete_after=delete_after, **kwargs)


class Rapport(Message):
    """envois un Rapport de commande"""

    def __init__(self, guild) -> None:
        super().__init__(TYPE.RAPPORT)

        self.chan = guild.get_channel(self.chan)
    

    async def process(self, send, message: str, delete_after=constants.TIMER, logger= None, logchan= None, **kwargs):
        if logger:
            logger.info(message)
        m  = await super().process(send, message, delete_after=delete_after, **kwargs)
        if logchan:
            await self.chan.send(embed=self.embed)
        return m


class Error(Message):
    def __init__(self, ctx, error, logger) -> None:
        super().__init__(TYPE.ERROR)
    
        self.ctx = ctx
        self.error = error
        self.logger = logger
    
    async def process(self, send, message: str, delete_after=constants.TIMER, **kwargs):
        
        self.logger.info(f"la commande {self.ctx.command} lancer par {self.ctx.author.display_name}"
        f"à provoquer l'erreur {self.error}")
        return await super().process(send, message, delete_after=delete_after, **kwargs)


class Cancel(Message):
    def __init__(self) -> None:
        super().__init__(TYPE.CANCEL)


class Moderation(Message):

    def __init__(self, type, ctx, logger) -> None:
        super().__init__(type)
        
        self.chan = ctx.guild.get_channel(self.chan)
        self.logger = logger
        self.ctx = ctx

        self.set_author(ctx.author.display_name, ctx.author.avatar.url)
    

    def makeEmbed(self):
        return discord.Embed(title=self.type.title, color=self.type.color)
    

    async def process(self, target: discord.User, reason: str, delete_after=constants.TIMER, send=None, **kwargs):
        if send is None:
            send = self.ctx.send

        message = self.type.action + target.display_name
        avatar_url = target.display_avatar.url if target.display_avatar else IMGURL.NotFound
        reason = 'raison : ' + reason

        self.logger.info(f"{self.type.title}: {self.author} - {message} - {reason}")
        self.embed.set_thumbnail(url=avatar_url)
        self.embed.add_field(name=message, value=reason, inline=False)

        await self.chan.send(embed=self.embed)

        return await self.ctx.send(embed=self.embed, delete_after=delete_after, **kwargs)


class AskButton(Message):
    def __init__(self, view) -> None:
        super().__init__(TYPE.CONFIRM)
        self.view = view
    

    async def process(self,send, message:str, delete_after=constants.TIMER, **kwargs):
        
        self.embed.description = message
        return await send(embed=self.embed, view=self.view, delete_after=delete_after, **kwargs)


class AskSelect(Message):
    def __init__(self, view) -> None:
        super().__init__(TYPE.SELECT)
    
        self.view = view
    
    async def process(self,send, message:str, delete_after=constants.TIMER, **kwargs):
        
        self.embed.description = message
        return await send(embed=self.embed, view=self.view, delete_after=delete_after, **kwargs)


def make_confirm_btn(ctx, btn1='confirmer', btn2='annuler', timeout=constants.ASK_TIMER):
    class DefaultButtonView(discord.ui.View):
        def __init__(self, *items, timeout: Optional[float] = 180):
            super().__init__(*items, timeout=timeout)

        @discord.ui.button(label=btn1, style=discord.ButtonStyle.green)
        async def first_callback(self, button, interaction: discord.Interaction):
            await interaction.response.edit_message(view=None)
            self.value = 1
            self.stop()
        
        @discord.ui.button(label=btn2, style=discord.ButtonStyle.red)
        async def second_callback(self, button, interaction: discord.Interaction):
            await interaction.response.edit_message(view=None)
            self.value = 0
            self.stop()

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.user != ctx.author:
                await interaction.response.send_message("vous ne pouvez pas utiliser ce bouton", ephemeral=True)
                return False
            return True
        
        async def on_timeout(self) -> None:
            self.value = 2
    
    return DefaultButtonView(timeout=timeout)