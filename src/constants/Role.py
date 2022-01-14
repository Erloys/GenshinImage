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
    """stock les id des roles"""
    
    MODERATOR = ROLE_ID['moderator']
    ADMIN = ROLE_ID['admin']
    """MEMBER ROLE: pour les admins"""
    OWNER = ROLE_ID['owner']
    """MEMBER ROLE: pour l'owner"""
    BOT = ROLE_ID['bot']
    """MEMBER ROLE: pour les bots"""


    VALID = ROLE_ID['valid']
    """MEMBER ROLE: role pour les personne autoriser a poster des images"""

    VISITOR = ROLE_ID['visitor']
    """MEMBER ROLE: peut seulement voir les images mais pas en poster"""

    EVERYONE = ROLE_ID['everyone']
    """DEFAULT ROLE: role que tout le monde à par défaut"""

    SAFE = ROLE_ID['safe']
    """CHANNEL ROLE: role pour accèder aux channels SAFE"""
    HOT = ROLE_ID['hot']
    """CHANNEL ROLE: role pour accèder aux channels HOT"""
    NSFW = ROLE_ID['nsfw']
    """CHANNEL ROLE: role pour accèder au channels NSFW"""

    DECO_MEMBER = ROLE_ID['decorator_member']
    """DECORATOR ROLE"""
    DECO_CHANNEL = ROLE_ID['decorator_channel']
    """DECORATOR ROLE"""


STAFF_ROLES = [roles.MODERATOR, roles.ADMIN, roles.OWNER]