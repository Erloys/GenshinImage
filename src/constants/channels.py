"""Constant liΓ©e aux channel"""

from discord import role
from .Role import roles

LOGCHAN = 922492857007341568
"""ID du channel de log"""
ARCHIVE = 800042738623840278
"""id du channel d'archive d'image"""

CONFIRM_CHAN = 919487889719570432
"""id du channel de validation doublon"""

LOG_CONFIRM = 918358853463183430


class MetaEnum(type):
    def __contains__(cls, x):
        return x in [cls.SAFE, cls.HOT, cls.NSFW]

    def __iter__(cls):
        for attr, value in cls.__dict__.items():
            if not attr.startswith("__"):
                yield value


class CHANNEL_TYPE(metaclass=MetaEnum):
    SAFE = "β"
    HOT = "π₯"
    NSFW = "π"


CH_TO_ROLE = {
    "β": roles.SAFE,
    "π₯": roles.HOT,
    "π": roles.NSFW
}