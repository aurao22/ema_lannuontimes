import scrapping_tregor as tregor
import scrapping_30_millions_amis as amis30
from scrapping_util import save_article_in_bdd
import news_paper_dao as np_dao
from os import getcwd
   

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                              CHARGEMENT INITIAL
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def load_articles(papers=["Le Trégor", "30 M. d'AMIS"], nb_articles=500, verbose = 0):
    """Save articles in BDD

    Args:
        verbose (int, optional): log level. Defaults to 0.
    """
    # Récupère le répertoire du programme
    curent_path = getcwd() +"\\"
    if "ema_lannuontimes" not in curent_path:
        curent_path += "PROJETS\\ema_lannuontimes\\"
    if verbose:
        print(curent_path)
        print("Intialisation de la BDD...", end="")

    dao = np_dao.NewsPaperDao(nom_bdd=curent_path+"em_bdd.db")
    if not dao.test_connexion():
        raise Exception("Impossible de se connecter à la BDD")
    elif verbose:
        print("...... TERMINE")
    
    # Initialisation de la BDD
    dao.initialiser_bdd(drop_if_exist=False, verbose=verbose)

    if "Le Trégor" in papers :
        _load_tregor(dao, nb_articles=nb_articles, verbose=verbose)
    
    if "30 M. d'AMIS" in papers:
        _load_30_m_amis(dao, nb_articles=nb_articles, verbose=verbose)

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
            
            # On poursuit le traitement même si l'enregistrement d'un article pose problème
            try:
                res = save_article_in_bdd(dao=dao, journal=journal, art=art, verbose=verbose)
                
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

def _load_tregor(dao, nb_articles=500, verbose=0):
    ever_save = dao.get_articles_url(journal="Le Trégor")

    if verbose:
        print("TREGOR ==> Début du scrapping des articles...")
    
    articles = tregor.get_articles(dao=dao, nb_articles=nb_articles,exclude=ever_save,verbose=verbose)
    if articles is not None and len(articles)>0:
        res = save_articles_in_bdd(dao=dao, journal="Le Trégor", articles=articles, verbose=verbose)
    else:
        print("TREGOR ==> Aucun nouvel article...")
    
    if verbose:
        print("30 M. d'AMIS ==> Début du scrapping des articles...")

def _load_30_m_amis(dao, nb_articles=100, verbose=0):
    if verbose:
        print("30 M. d'AMIS ==> Début du scrapping des articles...")
    
    ever_save = dao.get_articles_url(journal="30 M. d'amis")
    articles = amis30.get_articles(dao=dao, nb_articles=nb_articles,exclude=ever_save,verbose=verbose)
    if articles is not None and len(articles)>0:
        res = save_articles_in_bdd(dao=dao, journal="30 M. d'amis", articles=articles, verbose=verbose)
    else:
        print("30 M. d'AMIS ==> Aucun nouvel article...")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                              TESTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == "__main__":
    verbose = 1
    load_articles(papers=["Le Trégor", "30 M. d'AMIS"],verbose=verbose)
    # load_articles(papers=["30 M. d'AMIS"],verbose=verbose)