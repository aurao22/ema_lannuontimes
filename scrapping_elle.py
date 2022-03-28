# Importation des bibliothèques nécessaire

from scrapping_util import get_page, get_selenium_firefox_driver, save_article_in_bdd
from selenium.webdriver.common.by import By
import time
import math

# Fonction permettant de récupérer les urls des derniers articles

def get_links(url='https://www.elle.fr/actu/fil-info/People',nb_articles=20, gecko_driver_path=None, verbose=0):
    """_summary_

    Args:
        url (str, optional): _description_. Defaults to 'https://www.elle.fr/actu/fil-info/People'.
        nb_articles (int, optional): _description_. Defaults to 20.
        gecko_driver_path (_type_, optional): _description_. Defaults to None.
        verbose (int, optional): _description_. Defaults to 0.

    Returns:
        _type_: _description_
    """
    driver = get_selenium_firefox_driver(url, gecko_driver_path=gecko_driver_path)

    time.sleep(5)

    stop_cookies = driver.find_element_by_id("didomi-notice-agree-button")
    stop_cookies.click()

    time.sleep(5)  

    elems = driver.find_elements(by=By.XPATH, value="//span/a[@href]")
    urls = set()

   

    i = 0
    while len(urls) < nb_articles and i < len(elems):
        urls.add(elems[i].get_attribute("href"))
        i+=1
    return urls

# Fonction récupérant les différents éléments importants de l'article

def get_article(url, verbose=0):
    addict = dict()
    
    page = get_page(url)
    
    #Récupération des titres
    title = page.find("h1").getText()
    addict["titre"] = title
    
    #Récupération des articles
    article = page.find('div', {'id' : 'text'}).getText()
   
    addict["texte"] = article.replace("\n", " ").replace("\xa0", " ")

    #Récupération de l'url
    addict["url"] = url
    
    #Récupération de la date
    date = page.find('span', {'class' : 'publication'}).getText().strip()
    addict["date_parution"] = date
    
    
    #Récupération de l'auteur
    author = page.find('span', {'class' : 'media-heading'}).getText().strip()
    addict["auteur"] = author
    
    #Inchangés
    addict["journal"] = "Elle"
    addict["tags"] = "People"
    return addict

def get_articles(dao=None, nb_articles=100, exclude=None, journal="Elle", gecko_driver_path=None, verbose = 0):
    """Charge tous articles, les sauvegarde en BDD si dao est renseigné

    Args:
        dao (_type_): _description_
        nb_articles (int, optional): _description_. Defaults to 100.
        exclude (_type_, optional): _description_. Defaults to None.
        journal (str, optional): _description_. Defaults to "Elle".
        verbose (int, optional): log level. Defaults to 0.

    Returns:
        list(dict): Papers and article list
    """
       
    articles_urls_to_scrapt = get_links(nb_articles = nb_articles,verbose=verbose, gecko_driver_path=gecko_driver_path)
    
    
    if verbose:
        print("Elle ==> Début du scrapping des articles")

    articles = []
    if exclude is None:
        exclude = []
    excluded = 0
    for url in articles_urls_to_scrapt:
        if url not in exclude:
            try:
                art = get_article(url, verbose=verbose)
                articles.append(art)

                if dao is not None:
                    # Ajout de l'article en BDD
                    added = save_article_in_bdd(dao=dao, journal=journal, art=art, verbose = verbose)
                    if not added:
                        print("Elle ==> ERROR : Article non ajouté en BDD --------------------------- !!")    
            except Exception as error:
                print("Elle ==> ERROR : ", error, " --------------------------- !!")
        else:
            excluded += 1
    if verbose:
        print(f"Elle ==> {len(articles)} articles and {excluded} exculded arcticles")
    return articles

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                              TESTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


if __name__ == "__main__":

    liste = []

    for url in get_links(gecko_driver_path=r"C:\Users\erwan\Downloads\geckodriver.exe"):
        liste.append(get_article(url))

    print(len(liste))