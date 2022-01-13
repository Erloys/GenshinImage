from collections import namedtuple
from io import BytesIO
import logging
from re import I
import sys
from typing import Optional

import discord
from discord.commands.commands import Option
from discord.commands.context import ApplicationContext
from discord.components import SelectOption
from discord.commands import permissions
from discord.embeds import EmptyEmbed
from discord.ext import commands

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
    @permissions.has_any_role(*constants.STAFF_ROLES)
    async def manage_role(self, ctx: ApplicationContext, member: discord.Member):
        try:
            find = (r for r in member.roles if r.id in [constants.roles.VISITOR, constants.roles.VALID, constants.roles.MODERATOR, constants.roles.ADMIN, constants.roles.BOT])
            old_role = next(find)
        except StopIteration:
            old_role = None

        author_staff_role = permission.check_permission(ctx.author, member, ctx.guild)
        roles = [constants.roles.BOT,constants.roles.ADMIN,constants.roles.MODERATOR,
        constants.roles.VALID, constants.roles.VISITOR]
        
        possible_role = []
        if author_staff_role.id == constants.roles.OWNER:
            possible_role = roles
        elif author_staff_role.id == constants.roles.ADMIN:
            possible_role = roles[2:]
        
        elif author_staff_role.id == constants.roles.MODERATOR:
            possible_role = roles[3:]
        
        if old_role and old_role.id in possible_role:
            possible_role.remove(old_role.id)

        possible_role = [SelectOption(label=ctx.guild.get_role(r).name, value=r) for r in possible_role]        


        class rolechoice(discord.ui.View):
            def __init__(self, *items, timeout: Optional[float] = 180):
                super().__init__(*items, timeout=timeout)

                self.value = None
            
            @discord.ui.select(
                placeholder='choisisser le role à appliquer',
                min_values=1,
                max_values=1,
                options=possible_role
            )
            async def select_callback(self, select, interaction: discord.Interaction):
                await interaction.response.edit_message(view=None)
                self.value = select.values[0]
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
        
        role = ctx.guild.get_role(int(choices.value))
        if old_role:
            await member.remove_roles(old_role)
        await member.add_roles(role)

        fb = BotInteraction.Moderation(BotInteraction.ROLE_UPDATE, ctx, self.logger)
        fb.set_footer(f'{old_role.name} -> {role.name}', img=member.display_avatar.url)
        await fb.process(member, reason='undefined', send=ctx.send_followup)


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

        b = BotInteraction.make_confirm_btn(ctx)
        ask_confirm = BotInteraction.AskButton(view=b)

        await ask_confirm.process(ask_message.edit_original_message, f"confirmer la révocation du ban de {user.display_name}", delete_after=None)
        await b.wait()
        await ask_message.delete_original_message()

        if not b.value:
            raise constants.CancelError()

        await ctx.guild.unban(user)
        fb = BotInteraction.Moderation(BotInteraction.UNBAN, ctx, self.logger)
        await fb.process(user, reason="undefined")
    
    @commands.slash_command(guild_ids=[constants.SERVEUR_ID])
    async def ban(self, ctx: ApplicationContext,
    user: Option(discord.Member, description="cible de la commande", required=True),
    reason: Option(str, description='raison du bannissement', required=False) = "undefined"):
        """banni la cible"""

        utils.check_user(user)
        permission.check_permission(ctx.author, user, ctx.guild)

        v = BotInteraction.make_confirm_btn(ctx)
        fb = BotInteraction.AskButton(v)
        await fb.process(ctx.send_response, f"confirmer le bannissement de {user.display_name} pour : {reason}")

        await v.wait()

        if v == 2:
            raise constants.CancelError("temps écouler")

        elif v == 0:
            raise constants.CancelError
        else:
            await user.ban(reason=reason)

            fb = BotInteraction.Moderation(BotInteraction.BAN, ctx, self.logger)
            await fb.process(user, reason)
    
    @commands.slash_command(guild_ids=[constants.SERVEUR_ID])
    async def kick(self, ctx: ApplicationContext,
    user: Option(discord.Member, description="cible de la commande", required=True),
    reason: Option(str, description="raison de l'expulsion", required=False) = "undefined"):
        """expulse la cible"""

        utils.check_user(user)
        permission.check_permission(ctx.author, user, ctx.guild)

        v = BotInteraction.make_confirm_btn(ctx)
        fb = BotInteraction.AskButton(v)
        await fb.process(ctx.send_response, f"confirmer l'expulsion de {user.display_name} pour : {reason}")

        await v.wait()

        if v == 2:
            raise constants.CancelError("temps écouler")

        elif v == 0:
            raise constants.CancelError
        else:
            await user.kick(reason=reason)

            fb = BotInteraction.Moderation(BotInteraction.KICK, ctx, self.logger)
            await fb.process(user, reason)

    
    @commands.message_command(guild_ids=[constants.SERVEUR_ID])
    async def manage_doublon(self, ctx: ApplicationContext, message: discord.Message):
        if message.author != self.client.user:
            raise constants.CancelError('seul les message en attente de validation peuvent être cibler par cette commande')
        
        elif message.channel.id != constants.channels.CONFIRM_CHAN:
            raise constants.CancelError('seul les message du channel de validation peuvent être cibler par cette commande')
        
        elif not '@' in message.embeds[0].footer.text:
            raise constants.CancelError('seul les message en attente de validation peuvent être cibler par cette commande')
        
        v = BotInteraction.make_confirm_btn(ctx, btn1='✅ Valider', btn2='❌ Rejeter')
        fb = BotInteraction.AskButton(v)
        interaction = await fb.process(ctx.send_response, "que faire de l'image ?", delete_after=None)

        await v.wait()
        await interaction.delete_original_message()

        channel, msg = message.embeds[0].footer.text.split('@')
        channel = message.guild.get_channel(int(channel))
        msg = channel.get_partial_message(msg)
        msg = await msg.fetch()

        if v.value == 2:
            raise constants.CancelError('temps écouler')
        
        elif v.value == 0:
            text = "l'image à était ❌ rejeter"
            await utils.delete(self.client, msg)
        
        else:
            text = "l'image à était ✅ valider"
            img = BytesIO()
            await msg.attachments[0].save(img)
            hash = image_handler.get_hash(img)
            img.seek(0)
            path = image_handler.id_to_path(msg.jump_url)
            index = image_handler.Index(str(hash), msg.channel.name, msg.jump_url)
            self.database.add_image(index, img.read(), path)


        embed = message.embeds[0]
        embed.set_footer(text=text)
        embed.description = f"doublon traité par {ctx.author.display_name}"
        await message.delete()
        await message.channel.send(embed=embed)