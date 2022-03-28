from urllib import request
import bs4
from selenium import webdriver
import time
from os import environ
import news_paper_dao as np_dao

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                              COMMON SCRAPPING
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

def get_page_links(page, base_url="", class_=None, liste_urls=None, verbose=0):
    """Return all page or section links
    Args:
        page (BeautifulSoup): the page or the section of the page
        base_url (str, optional): the url base. Defaults to "".
        class_ (str, optional): The link class. Defaults to None.
        liste_urls (set(str), optional): The url list to complete. Defaults to None.
        verbose (int, optional): log level. Defaults to 0.

    Raises:
        AttributeError: if page is None

    Returns:
        set(str): link list
    """
    if page is None:
        raise AttributeError("page expected")
    
    if liste_urls is None:
        liste_urls =set()
    nb_url_start = len(liste_urls)
    liens_list = page.findAll('a')
    if class_ is None:
        liens_list = page.findAll('a')
    else:
        liens_list = page.findAll('a', {'class': class_})
    
    # Récupération de tous les liens de la page
    for lien in liens_list:
        link = lien.get('href')
        if base_url is not None and len(base_url) >0 and base_url not in link:
            link = base_url+link
        liste_urls.add(link)
    
    if verbose>1:
        print(len(liste_urls)-nb_url_start, " URLs found")
    return liste_urls

def get_selenium_firefox_driver(url, gecko_driver_path=None, verbose=0):
    """Create and return the firefox driver for selenium

    Args:
        url (str): URL to load
        gecko_driver_path (str, optional): the path to the gecko_driver. Defaults to None, so use the environnement variable : `GECKO_DRIVER_PATH`.
        verbose (int, optional): log level. Defaults to 0.

    Returns:
        WebDriver: firefox webdriver
    """
    if gecko_driver_path is None:
        if verbose:
            print('get_selenium_driver > No Gecko driver path, so use the environnement variable : `GECKO_DRIVER_PATH`')
        gecko_driver_path = environ.get('GECKO_DRIVER_PATH')
        if gecko_driver_path is None:
            raise Exception("No `GECKO_DRIVER_PATH` environment varibale define. This variable is mandatory to use selenium on firefox")
    driver = webdriver.Firefox(executable_path=gecko_driver_path)
    driver.get(url)
    time.sleep(5)
    return driver


def save_article_in_bdd(dao, journal, art, verbose = 0):
    """
    Save articles in BDD
    Args:
        dao (NewsPaperDao): dao
        journal (str) : journal name
        article (dict) : article
        verbose (int, optional): log level. Defaults to 0.

    Returns:
        int : nb added articles
    """
    res = 0  
    if art is not None and dao is not None:
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
        except Exception as error:
            print(f"{journal} ==> ERROR ==> Error lors de l'ajout de l'article : {art}", error)
            print(error)
            raise error
      
    return res
    


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                              TESTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == "__main__":
    verbose = 1
    pass