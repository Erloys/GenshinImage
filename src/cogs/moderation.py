from collections import namedtuple
import logging
import sys
from typing import Optional

import discord
from discord.commands.commands import Option, slash_command
from discord.commands.context import ApplicationContext
from discord.components import SelectOption
from discord.ext import commands
from discord.guild import BanEntry
from discord.utils import get
from discord.ui import select

sys.path.append("/data/projets/discord/src/")
import constants
import utils
import image_handler
import BotInteraction
import permission



class Moderation(commands.Cog):
    
    
    ban_list: list[str] = []

    f = lambda : ban_list

    def __init__(self, client: discord.Bot, database: image_handler.ImgHandler, logger: logging.Logger) -> None:
        self.client = client
        self.database = database
        self.logger = logger

    

    async def fb_rapport(self, ctx, message):
        fb = BotInteraction.Rapport(ctx.guild)

        await fb.process(ctx.send, message, logger=self.logger)
    

    async def fb_mod(self, type, ctx, target, reason):
        fb = BotInteraction.Moderation(type, ctx, self.logger)
        await fb.process(target, reason)

    @commands.user_command(guild_ids=[constants.SERVEUR_ID])
    async def manage_role(self, ctx: ApplicationContext, member: discord.Member):
        find = (r for r in member.roles if r.id in [constants.roles.VISITOR, constants.roles.VALID, constants.roles.MODERATOR, constants.roles.ADMIN, constants.roles.BOT])
        old_role = next(find)
        r = await permission.target_permission(ctx.author, member, ctx.guild)

        possible_roles = []
        if r.id == constants.roles.OWNER:
            possible_roles.append(SelectOption(label='💫 | Admin', value=constants.roles.ADMIN))
            possible_roles.append(SelectOption(label='🤖 | Bots', value=constants.roles.BOT))
        
        elif r.id in [constants.roles.ADMIN, constants.roles.OWNER]:
            possible_roles.append(SelectOption(label="‍🎓 | Modérateur", value=constants.roles.MODERATOR) )
        
        possible_roles.append(SelectOption(label='✔️ | Vérifié', value=constants.roles.VALID))
        possible_roles.append(SelectOption(label="🆕  | Visiteur", value=constants.roles.VISITOR))

        class rolechoice(discord.ui.View):
            def __init__(self, *items, timeout: Optional[float] = 180):
                super().__init__(*items, timeout=timeout)

                self.value = None
            
            @discord.ui.select(
                placeholder='choisisser le role à appliquer',
                min_values=1,
                max_values=1,
                options=possible_roles
            )
            async def select_callback(self, select, interaction: discord.Interaction):
                await interaction.response.edit_message(view=None)
                self.value = select.value
                self.stop()
            
            async def interaction_check(self, interaction: discord.Interaction) -> bool:
                if interaction.user != ctx.author:
                    fb = BotInteraction.Rapport(ctx.guild)
                    await fb.process(interaction.response.send_message, "cette interactions ne vous est pas déstiner", ephemeral=True)
                    return False
                return True


        choices = rolechoice(timeout=constants.ASK_TIMER)
        fb = BotInteraction.AskSelect(choices)
        ask_select = await fb.process(ctx.respond, f"manage role opened by {ctx.author.display_name}")
        await choices.wait()
        if not choices.value:
            raise constants.CancelError
        
        role = ctx.guild.get_role(choices.value)
        await member.remove_roles(old_role)
        await member.add_roles(role)

        fb = BotInteraction.Rapport(ctx.guild)
        fb.set_footer(f'{old_role.name} -> {role.name}', img=member.avatar.url)
        fb.process(ctx.send_followup, f"{ctx.author.display_name} à mise à jour les roles de {member.display_name}")


    @commands.slash_command(name='unban', guild_ids=[constants.SERVEUR_ID])
    @commands.has_any_role(constants.roles.MODERATOR, constants.roles.ADMIN)
    async def unban(self, ctx : ApplicationContext):
        
        choices = await utils.create_unban_choice(self.client)
        if len(choices) == 0:
            raise constants.CancelError("pas d'utilisateur bannis en ce momment")

        class unbanchoice(discord.ui.View):
            def __init__(self, *items, timeout: Optional[float] = 180):
                super().__init__(*items, timeout=timeout)

            self.value = None

            @discord.ui.select(
                placeholder="choisi l'utilisateur à unban",
                min_values=1,
                max_values=1,
                options=choices)
            async def select_callback(self, select, interaction: discord.Interaction):
                await interaction.response.edit_message(view=None)
                self.value = select.values[0]
                self.stop()
            

            async def interaction_check(self, interaction: discord.Interaction) -> bool:
                if interaction.user != ctx.author:
                    fb = BotInteraction.Rapport(ctx.guild)
                    fb.process(interaction.response.send_message, "ce message ne vous est pas déstiner", ephemeral=True)
                    return False
                return True
            
            async def on_timeout(self) -> None:
                self.value = None
                
        
        v =unbanchoice(timeout=constants.ASK_TIMER)
        ask_select = BotInteraction.AskSelect(view=v)

        ask_message = await ask_select.process(ctx.send_response, "choisissez l'utilisateur à unban", delete_after=None)
        
        await v.wait()

        if not v.value:
            await ask_message.delete_original_message()
            raise constants.CancelError
        user = await self.client.fetch_user(int(v.value))
        b = BotInteraction.DefaultButtonView(ctx, timeout=constants.ASK_TIMER)
        ask_confirm = BotInteraction.AskButton(view=b)

        ask_message2  = await ask_confirm.process(ask_message.edit_original_message, f"confirmer la révocation du ban de {user.display_name}", delete_after=None)
        await b.wait()
        await ask_message.delete_original_message()

        if b.value:
            await ctx.guild.unban(user)

            fb = BotInteraction.Moderation(BotInteraction.UNBAN, ctx, self.logger)
            await fb.process(user, reason="undefined")
        else:
            raise constants.CancelError()