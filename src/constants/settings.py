"""constants pour TOKEN et divers parametres (timer, owner_id, serveur_id)"""

OWNER_ID = 186537861321850880
SERVEUR_ID = 930342267091320853

TIMER = 7
ASK_TIMER = 10
DIR_PATH = "/data/projets/genshinImage/bot/"

class CancelError(Exception):
    """ À lever pour annuler une commande le text passé en argument sera envoyer dans le message d'annulation"""
    pass


