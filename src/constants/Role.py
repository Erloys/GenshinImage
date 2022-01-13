from typing import OrderedDict
from .settings import DIR_PATH, SERVEUR_ID

ROLE_ID: dict[str, int] = {}
"""prend en  clé le nom du role renvois son id"""
"""constant liée aux roles"""

with open(DIR_PATH + f"macro_data/{SERVEUR_ID}", "r") as f:
    roles = f.read()
roles = roles.split("\n")
for roles in roles:
    name, id = roles.split("@")
    ROLE_ID[name] = int(id)


class roles:
    MODERATOR = ROLE_ID['moderator']
    ADMIN = ROLE_ID['admin']
    OWNER = ROLE_ID['owner']
    BOT = ROLE_ID['bot']
    SAFE = ROLE_ID['safe']
    HOT = ROLE_ID['hot']
    NSFW = ROLE_ID['nsfw']
    DECO_MEMBER = ROLE_ID['decorator_member']
    DECO_CHANNEL = ROLE_ID['decorator_channel']
    VISITOR = ROLE_ID['visitor']
    VALID = ROLE_ID['valid']


STAFF_ROLES = [roles.MODERATOR, roles.ADMIN, roles.OWNER]