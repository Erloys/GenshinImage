"""Constant liée aux channel"""

from discord import role
from .Role import roles

LOGCHAN = 930342267917594651
"""ID du channel de log"""
ARCHIVE = 930342267917594652
"""id du channel d'archive d'image"""


class MetaEnum(type):
    def __contains__(cls, x):
        return x in [cls.SAFE, cls.HOT, cls.NSFW]

    def __iter__(cls):
        for attr, value in cls.__dict__.items():
            if not attr.startswith("__"):
                yield value


class CH_TYPE(metaclass=MetaEnum):
    SAFE = "✅"
    HOT = "🔥"
    NSFW = "🔞"


CH_TO_ROLE = {
    "✅": roles.SAFE,
    "🔥": roles.HOT,
    "🔞": roles.NSFW
}