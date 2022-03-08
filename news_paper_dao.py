import sqlite3
from os import getcwd, remove, path

class NewsPaperDao():

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

    def liste_tables(self, verbose=False):
        """ Liste les tables existants dans la BDD

        Args:
            verbose (bool/int, optional): Niveau de détail pour les traces. Defaults to False.

        Returns:
            List: Retourne la liste des tables créées dans la BDD
        """
        tables = self._executer_sql("SELECT name FROM sqlite_master WHERE type='table';", verbose=verbose)
        tables_name = []
        for it in tables:
            tables_name.append(it[0])
        return tables_name

    def nombre_articles(self, journal=None, verbose=False):
        """Compte le nombre d'articles en BDD

        Args:
            journal (str, optional) : Nom du journal, si aucun, nombre total d'articles
            verbose (bool/int, optional): Niveau de détail pour les traces. Defaults to False.

        Returns:
            int: le nombre d'articles en BDD
        """
        sql = "SELECT count(*) FROM `article`"
        if journal is not None:
            sql = f"{sql} WHERE `journal`='{journal}'"
        res = self._executer_sql(sql+";", verbose=verbose)
        
        if verbose:
            print(res[0][0])
        # on retourne la 1ère valeur de la 1ère ligne
        return res[0][0]

    def nombre_journaux(self, verbose=0):
        """Compte le nombre de journaux en BDD

        Args:
            verbose (bool/int, optional): Niveau de détail pour les traces. Defaults to 0.

        Returns:
            int: le nombre de journaux en BDD
        """
        sql = "SELECT count(*) FROM `journal`"
        res = self._executer_sql(sql+";", verbose=verbose)
        
        if verbose:
            print(res[0][0])
        # on retourne la 1ère valeur de la 1ère ligne
        return res[0][0]

    def ajouter_journal(self, nom, frequence, fondateur=None, site=None, articles_page=None, verbose=0):
        """Ajoute un journal en BDD

        Args:
            nom (str): _description_
            frequence (str): _description_
            fondateur (str, optional): _description_. Defaults to None.
            site (str, optional): _description_. Defaults to None.
            articles_page (str, optional): _description_. Defaults to None.
            verbose (int, optional): log level. Defaults to 0.

        Raises:
            TypeError: Lorsque la station n'est pas de type :Station ou list[Station] ou dict{-:Station}
            ValueError: Lorsque la station vaut None

        Returns:
           (str): Identifiant
        """
        res = None
        if nom is not None and isinstance(nom, str):   
            # INSERT OR IGNORE pour éviter des doublons, logiquement devrait éviter d'avoir l'exception IntegrityError
            sql = f"INSERT OR IGNORE INTO `journal` (`nom`, `fondateur`, `frequence`, `site_web`, `url_articles`) VALUES ('{nom}','{fondateur}','{frequence}','{site}','{articles_page}');"
            res = self._executer_sql(sql, verbose=verbose)
        else:
            raise ValueError(f"Attendu nom journal str, reçu {nom}")
        return res

    def ajouter_article(self, titre, date_parution, texte, journal, auteur=None, url=None, tags=None, verbose=0):
        """Ajoute un article

        Args:
            titre (str): Titre de l'article
            date_parution (str): date de parution
            texte (str): contenu de l'article
            journal (str): nom du journal
            url (str, optional): url de l'article. Defaults to None.
            auteur (str, optional): auteur. Defaults to None.
            tags (str, optional): _description_. Defaults to None.
            verbose (bool/int, optional): log level. Defaults to 0

        Raises:
            TypeError: _description_
            ValueError: _description_

        Returns:
            int: identifiant de l'article ajouté
        """   
        res = None
        if titre is not None and date_parution is not None and texte is not None and journal is not None:

            # pre-traitement
            titre = _sql_str_preprocess(titre)
            date_parution = _sql_str_preprocess(date_parution)
            journal = _sql_str_preprocess(journal)
            texte = _sql_str_preprocess(texte)
            
            # On vérifie si l'article n'existe pas déjà
            sql = f'SELECT count(`id`) FROM `article` WHERE `titre`="{titre}" AND `date_parution`="{date_parution}" AND `journal`="{journal}"'
            if verbose:
                print(sql)
            res = self._executer_sql(sql, verbose=verbose)
            exist = res[0][0] > 0

            if not exist:
                sql_start = "`id`,`titre`,`date_parution`, `texte`, `journal`"
                sql_end = f'NULL, "{titre}", "{date_parution}","{texte}", "{journal}"'

                if auteur is not None and len(auteur)>0:
                    sql_start += ", `auteur`"
                    auteur = _sql_str_preprocess(auteur)
                    sql_end += f', "{auteur}"'

                if url is not None and len(url)>0:
                    sql_start += ", `url`"
                    url = _sql_str_preprocess(url)
                    sql_end += f', "{url}"'

                if tags is not None and len(tags)>0:
                    sql_start += ", `tags`"
                    tags = _sql_str_preprocess(tags)
                    sql_end += f', "{tags}"'

                sql = 'INSERT INTO `article` (' + sql_start +')  VALUES ('+ sql_end+');'

                res = self._executer_sql(sql, verbose=verbose)
            else:
                return False
            
        else:
            raise ValueError(f"titre, date_parution, texte and journal ar mandatory, receive : {titre}, {date_parution}, {texte} and {journal}")
        return res

    def articles(self, journal=None, verbose=0):
        """_summary_

        Args:
            journal (_type_, optional): _description_. Defaults to None.
            verbose (int, optional): _description_. Defaults to 0.

        Returns:
            _type_: _description_
        """
        sql = "SELECT * FROM `article` "
        if journal is not None and len(journal)>0:
            sql += f" WHERE `journal` = '{journal}'"

        res = self._executer_sql(sql+" ORDER BY id;", verbose=verbose)
        return res

    def get_articles_url(self, journal=None, verbose=0):
        """_summary_

        Args:
            journal (_type_, optional): _description_. Defaults to None.
            verbose (int, optional): _description_. Defaults to 0.

        Returns:
            _type_: _description_
        """
        sql = "SELECT distinct(`url`) FROM `article` "
        if journal is not None and len(journal)>0:
            sql += f" WHERE `journal` = '{journal}'"

        res = self._executer_sql(sql+"ORDER BY id ;", verbose=verbose)
        url_list = []
        if res is not None and isinstance(res, list):
            for tu in res:
                url_list.append(tu[0])
        return url_list
   

    def initialiser_bdd(self, drop_if_exist = False, verbose=False):
        """Créé les tables manquantes

        Args:
            drop_if_exist (bool, optional): Pour supprimer les tables si elles existent déjà /!\ Suppression des données. Defaults to False.
            verbose (bool/int, optional): Niveau de détail pour les traces. Defaults to False

        Returns:
            bool: Si les tables existent dans la BDD ou non
        """
        if drop_if_exist:
            self._supprimer_table_article(verbose)
            self._supprimer_table_journal(verbose)
        # Vérifier si la BDD existe déjà
        tables = self.liste_tables(verbose)
        if "journal" not in tables:
            self._creer_table_journal(verbose)
            self._insert_journaux(verbose)
        if "article" not in tables:
            self._creer_table_article(verbose)
        # vérifier que les tables sont bien créées
        tables = self.liste_tables(verbose)
        return "journal" in tables and "article" in tables

    def creer_sauvegarde(self, file_path, verbose=False):
        """Créer un fichier de sauvegarde de la BDD courante

        Args:
            file_path (str): Chemin complet avec nom du fichier de la sauvegarde
            verbose (bool/int, optional): Niveau de détail pour les traces. Defaults to False

        Returns:
            boolean: True si fichier de sauvegarde créé, False sinon
        """
        success = False
        try:
            conn = self.connecter()
            BDD_Destination = sqlite3.connect (file_path)
            conn.backup (BDD_Destination)
            if verbose:
                print("SQLite DAO > Sauvegarde effectuée :",file_path)
        # Fermeture des connexions
        finally:
            try:
                BDD_Destination.close()
                if verbose > 1:
                    print("SQLite DAO > connexion sauvegarde fermée")
            except Exception:
                pass
            try:
                conn.close()
                if verbose > 1:
                    print("SQLite DAO > La connexion est fermée")
            except Exception:
                pass
        # Vérification que le fichier existe bien
        try:
            with open(file_path): success=True
        except IOError:
            pass   
        return success

    def _supprimer_table_journal(self, verbose=False):
        res = self._executer_sql("DROP TABLE IF EXISTS `journal`;", verbose=verbose)
        return res

    def _supprimer_table_article(self, verbose=False):
        res = self._executer_sql("DROP TABLE IF EXISTS `article`;", verbose=verbose)
        return res

    def _creer_table_journal(self, verbose=False):
        sql = """CREATE TABLE IF NOT EXISTS `journal`(  
                `nom` TEXT NOT NULL PRIMARY KEY,
                `fondateur` TEXT,
                `frequence` TEXT,
                `site_web` TEXT,
                `url_articles` TEXT
            );
            """
        res = self._executer_sql(sql, verbose=verbose)
        return res

    def _insert_journaux(self, verbose=0):
        sql ="""INSERT OR IGNORE INTO journal(nom,fondateur,frequence,site_web,url_articles) VALUES 
        ('Le Trégor','Stéphane Le Tyrant','hebdomadaire','https://actu.fr/le-tregor/','https://actu.fr/le-tregor/dernieres-actus'),
        ('ActuGaming','Julien Blary','aleatoire', 'https://www.actugaming.net/','https://www.actugaming.net/actualites/'),
        ('Elle','Hélène Lazareff','aleatoire','https://www.elle.fr/','https://www.elle.fr/actu/fil-info/People');
        """
        res = self._executer_sql(sql, verbose=verbose)
        return res

    def _creer_table_article(self, verbose=False):
        sql = """
        CREATE TABLE IF NOT EXISTS `article`(  
                `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                `titre` TEXT NOT NULL,
                `date_parution` TEXT NOT NULL,
                `texte` TEXT NOT NULL,
                `auteur` TEXT,
                `tags` TEXT,
                `url` TEXT,
                `journal` TEXT NOT NULL,
                FOREIGN KEY(`journal`) references journal(`nom`)
            );
        """
        res = self._executer_sql(sql, verbose=verbose)
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


def _sql_str_preprocess(txt):
    txt = txt.replace("'", "\\'")
    txt = txt.replace('"', "\\'\\'")
    return txt

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                              TESTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def _remove_file(file_path):
    try:
        if path.exists(file_path):
            remove(file_path)
    except OSError as e:
        print(e)
   

if __name__ == "__main__":

    verbose = 1


    txt = 'Lannion. Léa Poplin, nouvelle sous-préfète : "Je suis là pour faire avancer les dossiers"'
    res = _sql_str_preprocess(txt)
    if verbose:
        print(txt)
        print(res)

    assert res == "Lannion. Léa Poplin, nouvelle sous-préfète : \\'\\'Je suis là pour faire avancer les dossiers\\'\\'"

    # Récupère le répertoire du programme
    curent_path = getcwd()+ "\\"
    if "ema_lannuontimes" not in curent_path:
        curent_path += "PROJETS\\ema_lannuontimes\\"
    print(curent_path)

    test_file_bdd = curent_path+'bdd_test.db'
    test_file_bdd_save = curent_path+"bdd_test_sauvegarde.db"
    
    # suppression du fichier s'il existe déjà (sinon les tests seront failed)
    _remove_file(test_file_bdd)

    ma_dao = NewsPaperDao(test_file_bdd)
    ma_dao.initialiser_bdd(drop_if_exist=True)

    assert ma_dao.test_connexion(verbose=verbose)
    # Création avec une BDD vide
    assert ma_dao.initialiser_bdd(verbose=verbose)
    res = ma_dao.liste_tables(verbose=verbose)
    print("liste des tables:",res)
    assert res is not None
    res = ma_dao.articles(verbose=verbose)
    print(res)
    assert res is not None
   
    
    # Suppression des fichiers de tests
    _remove_file(test_file_bdd)
    _remove_file(test_file_bdd.replace(".db", ".backup.db"))
    _remove_file(test_file_bdd_save)