from urllib import request
import bs4
from mysqlx import DatabaseError
import scrapping_tregor as tregor
import news_paper_dao as np_dao
from os import getcwd

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                              COMMON
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def get_page(url, verbose=0):
    """Retrieve the HTML page

    Args:
        url (str): the page URL
        verbose (int, optional): Log level. Defaults to 0.

    Returns:
        BeautifulSoup: the page
    """
    if verbose>1:
        print("Request url :", url)
    req = request.Request(url, headers = {'User-Agent' : 'Mozilla/5.0'})
    html = request.urlopen(req).read()
    return bs4.BeautifulSoup(html, "lxml")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                              CHARGEMENT INITIAL
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def load_articles(verbose = 0):
    """Save articles in BDD

    Args:
        verbose (int, optional): log level. Defaults to 0.
    """
    # Récupère le répertoire du programme
    curent_path = getcwd()+ "\\PROJETS\\ema_lannuontimes\\"
    if verbose:
        print(curent_path)
        print("Intialisation de la BDD...", end="")

    dao = np_dao.NewsPaperDao(nom_bdd=curent_path+"em_bdd.db")
    if not dao.test_connexion():
        raise DatabaseError("Impossible de se connecter à la BDD")
    elif verbose:
        print("...... TERMINE")
    
    # Initialisation de la BDD
    dao.initialiser_bdd(drop_if_exist=False, verbose=verbose)

    ever_save = dao.get_articles_url(journal="Le Trégor")

    if verbose:
        print("TREGOR ==> Début du scrapping des articles...")
    
    articles = tregor.get_articles(exclude=ever_save,verbose=verbose)
    if articles is not None and len(articles)>0:
        res = save_articles_in_bdd(dao=dao, journal="TREGOR", articles=articles, verbose=verbose)
    else:
        print("TREGOR ==> Aucun nouvel article...")
    
    # TODO Erwan : ajouter chargement des articles ELLE
    # TODO Mehdi : ajouter chargement des articles actugaming

def save_articles_in_bdd(dao, journal, articles, verbose = 0):
    """
    Save articles in BDD
    Args:
        dao (_type_): _description_
        journal (str) : journal name
        articles (list(dict)) : article list
        verbose (int, optional): log level. Defaults to 0.

    Returns:
        int : nb added articles
    """  
    if articles is not None and dao is not None:
        if verbose :
            print(f"{journal} ==> {len(articles)} récupérés....")
        nb_added_art = 0
        nb_ever_exist = 0
        for art in articles:
            titre=art.get("titre", None)
            date_parution=art.get("date_parution", None)
            texte=art.get("texte", None)
            journal=art.get("journal", None)
            auteur=art.get("auteur", None)

            # On poursuit le traitement même si l'enregistrement d'un article pose problème
            try:
                res = dao.ajouter_article(titre=titre,
                               date_parution=date_parution, 
                               texte=texte, 
                               journal=journal, 
                               auteur=auteur, 
                               url=art.get("url", None),
                               tags=art.get("tags", None),
                               verbose=verbose)
                if res:
                    nb_added_art += 1
                else:
                    nb_ever_exist += 1

            except Exception as error:
                print(f"{journal} ==> ERROR ==> Error lors de l'ajout de l'article : {_article_dic_to_str(art)}", error)
  
    if verbose:
        print(f"{journal} ==> {nb_added_art} articles chargés, {nb_ever_exist} articles déjà enregistrés")
    return nb_added_art

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Privates functions

def _article_dic_to_str(art):
    titre=art.get("titre", None)
    date_parution=art.get("date_parution", None)
    journal=art.get("journal", None)
    auteur=art.get("auteur", None)
    return f"{titre} du {date_parution} de {auteur} pour {journal}"


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                              TESTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == "__main__":
    verbose = 1
    load_articles(verbose=verbose)