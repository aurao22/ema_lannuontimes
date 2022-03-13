import sqlite3
from os import getcwd, remove, path
from news_paper_dao import *


class OldNewsPaperDao():

    def __init__(self, nom_bdd, backup_path=None):
        """Constructeur

        Args:
            nom_bdd (str): Chemin complet de la bdd
            backup_path (str, optional): Chemin complet pour le backup de la bdd. Defaults to None, le nom sera le même que celui de la BDD mais avec .backup.db.
        """
        self.nom_bdd = nom_bdd
        if backup_path is None:
            backup_path = self.nom_bdd.replace(".db", ".backup.db")
        self.backup_path = backup_path

    def connecter(self, verbose=False):
        """Connecte la base de données
        Args:
            verbose (bool/int, optional): Niveau de détail pour les traces. Defaults to False.

        Raises:
            error: En cas de problème établir la connexion à la BDD

        Returns:
            Connection: la connexion ouverte
        """
        conn = None
        try:
            conn = sqlite3.connect(self.nom_bdd)
        except sqlite3.Error as error:
            print("SQLite > Erreur de connexion à la BDD", error)
            try:
                if verbose > 1:
                    print("SQLite > La connexion est fermée")
                conn.close()
            except Exception:
                pass       
            raise error
        return conn


    def test_connexion(self, verbose=False):
        """Teste la connexion à la BDD

        Args:
            verbose (bool/int, optional): Niveau de détail pour les traces. Defaults to False.

        Returns:
            bool: True si le test a fonctionné, False sinon
        """
        try:
            sql = "SELECT sqlite_version();"       
            res = self._executer_sql(sql, verbose)
            print("La version de SQLite est: ", res)
            return True
        except sqlite3.Error as error:
            print("Erreur lors de la connexion à SQLite", error)
            return False

    

    def migrate_all_articles_and_insert(self, new_dao, verbose=0):
 
        res = None
        
        # On vérifie si l'article n'existe pas déjà
        sql = f'SELECT `url`,`titre`,`date_parution`, `texte`, `journal`, `auteur`, `tags` FROM `article`'
        if verbose:
            print(sql)
        res = self._executer_sql(sql, verbose=verbose)
        
        if res:
            # TODO insertion dans la BDD
            for art in res:
                #                       titre, date_parution, texte, journal,url, auteur=None,  tags=None, verbose=0
                new_dao.ajouter_article(url=art[0], titre=art[1], date_parution=art[2], texte=art[3],journal=art[4], auteur=art[5],  tags=art[6], verbose=verbose)
                pass

        return res

    def _executer_sql(self, sql, verbose=False):
        conn = None
        cur = None
        # Séparation des try / except pour différencier les erreurs
        try:
            conn = self.connecter()
            cur = conn.cursor()
            if verbose > 1:
                print("SQLite DAO > Base de données crée et correctement connectée à SQLite")
            try:
                if verbose:
                    print("SQLite DAO >", sql, end="")
                cur.execute(sql)
                conn.commit()
                if "INSERT" in sql:
                    res = cur.lastrowid
                else:
                    res = cur.fetchall()

                if verbose:
                    print(" =>",res)
            except sqlite3.Error as error:
                print("\nSQLite > Erreur exécution SQL:", sql, "\n", error)
                raise error
        except sqlite3.Error as error:
            print("SQLite > Erreur de connexion à la BDD", sql, "\n", error)
            raise error
        finally:
            try:
                if verbose > 1:
                    print("SQLite > Le curseur est fermé")
                cur.close()
            except Exception:
                pass
            try:
                if verbose > 1:
                    print("SQLite > La connexion est fermée")
                conn.close()
            except Exception:
                pass       
        return res


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                              TESTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  

if __name__ == "__main__":

    verbose = 1
    # Récupère le répertoire du programme
    curent_path = getcwd()+ "\\"
    if "ema_lannuontimes" not in curent_path:
        curent_path += "PROJETS\\ema_lannuontimes\\"
    print(curent_path)

    test_file_bdd_old = curent_path+'Z_OLD\\em_bdd_2022-03-09.db'
    test_file_bdd_new = curent_path+"em_bdd.db"


    ma_dao = NewsPaperDao(test_file_bdd_new)
    assert ma_dao.test_connexion(verbose=verbose)

    old_dao = OldNewsPaperDao(test_file_bdd_old)
    assert old_dao.test_connexion(verbose=verbose)
    
    old_dao.migrate_all_articles_and_insert(ma_dao, verbose=verbose)