"""constants pour TOKEN et divers parametres (timer, owner_id, serveur_id)"""

OWNER_ID = 186537861321850880
SERVEUR_ID = 305675798088777741

TIMER = 7
ASK_TIMER = 10
DIR_PATH = "/data/projets/genshinImage/bot/"
IMGPATH = DIR_PATH + "database/img/"

MARGE_DIFFERENCE = 15

class CancelError(Exception):
    """ À lever pour annuler une commande le text passé en argument sera envoyer dans le message d'annulation"""
    pass


