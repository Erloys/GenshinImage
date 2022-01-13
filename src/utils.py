import sys
from discord import channel
sys.path.append("/data/projets/discord/src/")

import requests
import discord
from discord.ext import commands
from imagehash import ImageHash

import constants
import image_handler


async def delete(client, message: discord.Message):
    """supprime le message"""

    if len(client.last_message_delete) >= 20:
        client.last_message_delete = []
    
    client.last_message_delete.append(message.id)

    await message.delete()



def isOwner(user, guild): return user == guild.owner or user.id == constants.OWNER_ID

def isAdmin(user, guild):
    role = guild.get_role(constants.roles.ADMIN)
    return role in user.roles


def isMod(user, guild):
    role = guild.get_role(constants.roles.MODERATOR)
    return role in user.roles

def isBot(user, guild):
    role = guild.get_role(constants.roles.BOT)
    return role in user.roles

def isStaff(user, guild):
    return isAdmin(user, guild) or isMod(user, guild) or isOwner(user, guild)


def getStaffRole(user, guild):
    if isOwner(user, guild):
        return guild.get_role(constants.roles.OWNER)

    roles = [None, constants.roles.MODERATOR, constants.roles.ADMIN, constants.roles.BOT, constants.roles.OWNER]
    found = None
    for i in user.roles:
        if i.id in roles and roles.index(i.id) > roles.index(found):
            found = i
    return found


def isUrl(text):
    try:
        requests.get(text)
    
    except Exception:
        return False
    
    else:
        return True


def isImgChan(name):
    return any(True for i in constants.channelsType if i in name)



def check_hash(
    data: list[image_handler.Index], hash: ImageHash
) -> list[image_handler.Index]:
    """renvois la liste d'index possédant des hash similaire au hash donnée
    si aucun similaire renvois une liste vide"""
    return [i for i in data if i.hash - hash < constants.MARGE_DIFFERENCE]


def check_user(user):
    """lève un `CANCEL ERROR` si la cible n'est pas accessible par le bot"""
    if type(user) is int:
        raise constants.CancelError(
            "oups je n'arrive pas à trouver l'utiliseur"
            " il ne se trouve pas dans ce serveur ?"
        )


async def create_unban_choice(client):
    guild = client.get_guild(constants.SERVEUR_ID)
    bans = await guild.bans()

    return [discord.SelectOption(label=b.user.display_name, value=str(b.user.id)) for b in bans]