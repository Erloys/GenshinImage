from collections import namedtuple
from contextlib import contextmanager
import logging
import os
import shutil
import sqlite3

import imagehash
from PIL import Image

import constants


Index = namedtuple('Index', "hash tag id")


def id_to_path(id:str) -> str:return id.split('/')[-1]

def get_hash(filelike):
    return imagehash.average_hash(Image.open(filelike), hash_size=10)

def check_hash(
    data: list[Index], hash: imagehash.ImageHash
) -> list[Index]:
    """renvois la liste d'index possédant des hash similaire au hash donnée
    si aucun similaire renvois une liste vide"""
    return [i for i in data if i.hash - hash < constants.MARGE_DIFFERENCE]



class ImgHandler:
    
    def __init__(self, db_name, logger: logging.Logger) -> None:

        self.con = sqlite3.connect(db_name)
        self.con.row_factory = sqlite3.Row
        self.logger = logger

        self.index_list : list[Index] = []
    

    @contextmanager
    def connect(self):
        try:
            a = self.con.cursor()
            yield a
        finally:
            a.close()


    def add_index(self, index: Index):
        """ajoute un index d'image à la database

        PARAMETER
        ---------

        index: :class:`Index`
                l'index à ajouter

        :raise: sqllite3.Error si peut pas accéder à la database
        """

        query = "INSERT INTO index_image (hash, tag, id) VALUES (?, ?, ?)"
        value = (index.hash, index.tag, index.id)

        with self.connect() as f:
            f.execute(query, value)

            self.logger.info(f"ajout de l'index {id} dans la database")
            self.con.commit()
        

    def edit_index(self, id: str, new_index: Index):
        """met à jour l'id cibler avec les nouvelle informations

        PARAMETER
        ---------

        id: :class:`str`
                id de l'index à modifier.

        new_index: :class:`Index`
                nouvelle information à appliquer.
        """

        with self.connect() as f:
            query = "UPDATE index_image SET id = ?, hash = ?, tag = ? \
            Where id = ?"
            value = (new_index.id, str(new_index.hash), new_index.tag, id)
            f.execute(query, value)
            self.con.commit()
    
    def delete_index(self, id: Index.id):
        """supprime un index par son id

        PARAMETER
        ---------

        id: :class:`str`
                id de l'index à supprimer
        """

        with self.connect() as f:
            query = "DELETE FROM index_image Where id = ?"
            value = (id,)
            f.execute(query, value)
            self.con.commit()

    def get_index(self) -> list[Index]:
        """Renvois la liste des index

        :raise: sqlite3.Error si peut pas accèder à la database
        """
        query = "SELECT COUNT(*) FROM index_image"

        with self.connect() as f:
            f.execute(query)
            res = f.fetchone()[0]

            if res != len(self.index_list):  # si oui on actualise les données
                query = "Select * FROM index_image"
                f.execute(query)
                res = f.fetchall()
                self.index_list = [
                    Index(
                        imagehash.hex_to_hash(dict(i)["hash"]),
                        dict(i)["tag"],
                        dict(i)["id"],
                    )
                    for i in res
                ]
                self.logger.info(
                    "actualisation de la base de donné en mémoire nouvelle "
                    f"taille -> {len(self.index_list)}"
                )
        return self.index_list

    def remove_index(self, id: str):
        """supprime l'index associer à l'id
        :raise: sqlite3.Error si peut pas accèder à la database
        """
        query = "DELETE FROM index_image WHERE id = ?"
        value = (id,)

        with self.connect() as f:
            print(f"accès à la database pour supprimer {id}")
            f.execute(query, value)
            cursor = self.con.cursor()
            cursor.execute(query, value)
            print(f"suppression de l'index {id[-18:]} de la database")
            self.con.commit()

    def add_image(self, index: Index, imgbyte, path):

        self.add_index(index)

        os.makedirs(os.path.dirname(constants.IMGPATH + path), exist_ok=True)
        with open(constants.IMGPATH + path, "wb") as f:
            f.write(imgbyte)
        self.logger.info(f"l'image {index.tag} à était ajouter à la base de donnée")

    def edit_image(self, path, new_path):
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        shutil.copy(path, new_path)
        os.remove(path)
        self.logger.info(f"limage {path} à était déplacer à {new_path}")

    def delete_image(self, path):
        try:
            os.remove(path)
        except OSError:
            raise constants.CancelError("l'index n'existe pas dans la database")

    def get_image(self, path) -> bytes:
        """Renvois l'image associer à l'id
        si image pas trouver supprime l'index associer à l'id et retourne une
        image d'erreur à la place"""
        filename = constants.IMGPATH + path
        try:
            with open(filename, "rb") as f:
                return f.read()

        except FileNotFoundError:
            self.remove_index(id)
            self.logger.warn(
                f"l'image {filename} n'existe pas"
                "son id à était retirer de l'index de la database"
            )
            with open(constants.IMGPATH + "404-error.jpg", "rb") as f:
                return f.read()