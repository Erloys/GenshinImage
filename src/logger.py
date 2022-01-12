import os
import sys
import logging
from datetime import datetime

sys.path.append('/data/projets/genshinImage/bot/src/')

import coloredlogs

import constants


def Make():
    logger = logging.getLogger("bot_logger")

    logger.setLevel(logging.INFO)

    directory = datetime.now().strftime("%d.%m.%Y")
    os.makedirs(constants.DIR_PATH + "logs/" + directory, exist_ok=True)
    file_name = "client.log"
    file = logging.FileHandler(
        constants.DIR_PATH + "logs/" + directory + "/" + file_name
    )
    file.setLevel(logging.DEBUG)
    format = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(funcName)s - file:%(filename)s "
        "line:%(lineno)d : %(message)s"
    )
    file.setFormatter(format)
    logger.addHandler(file)
    coloredlogs.install(
        "INFO",
        logger=logger,
        fmt="%(asctime)s - %(levelname)s -  %(message)s",
    )
    return logger