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



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                              TESTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


if __name__ == "__main__":

    liste = []

    for url in get_links(gecko_driver_path=r"C:\Users\erwan\Downloads\geckodriver.exe"):
        liste.append(get_article(url))

    print(len(liste))