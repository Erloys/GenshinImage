import discord
from discord.commands.permissions import is_owner

import constants
import utils


async def target_permission(a: discord.Member, b: discord.Member, guild: discord.Guild):
    author = utils.getStaffRole(a, guild)
    target = utils.getStaffRole(b, guild)

    target_is_staff = target != None
    if not target_is_staff:
        return author

    is_owner = author.id == constants.roles.OWNER
    is_admin = author.id == constants.roles.ADMIN
    
    target_is_Owner = target.id == constants.roles.OWNER
    target_is_bot = target.id == constants.roles.BOT
    target_is_admin = target.id == constants.roles.ADMIN and not is_owner
    target_is_moderator = target.id == constants.roles.MODERATOR and (not is_admin or is_owner)
    if target_is_Owner or target_is_admin or target_is_bot or target_is_moderator:
        raise constants.CancelError("vous ne possèder pas les permissions requises")
    
    
    return author