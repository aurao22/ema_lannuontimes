from scrapping_util import get_page, get_selenium_firefox_driver, save_article_in_bdd
from selenium.webdriver.common.by import By
import time
import math

def get_links(url="https://www.actugaming.net/actualites/", gecko_driver_path=None, nb_articles=20, verbose=0):
    driver = get_selenium_firefox_driver(url, gecko_driver_path=gecko_driver_path)
    refuse_btn = driver.find_element(by=By.CLASS_NAME, value='css-1g6dv8a')
    refuse_btn.click()
    load_more_btn = driver.find_element(by=By.CLASS_NAME, value='alm-load-more-btn')
    load_times = math.ceil((nb_articles - 12) / 8)
    for i in range(load_times):
        time.sleep(5)

        load_more_btn.click()
        

    time.sleep(5)
    elems = driver.find_elements(by=By.XPATH, value="//figure/a[@href]")
    urls = set()

    i = 0
    while len(urls) < nb_articles and i < len(elems):
        urls.add(elems[i].get_attribute("href"))
        i+=1

    return urls

def get_article(url, verbose=0):
    addict = dict()
    
    page = get_page(url)
    
    #Récupération des titres
    title = page.find("h1").getText()
    addict["titre"] = title
    
    #Récupération des articles
    article = page.find('div', {'id' : 'wtr-content'})
    if article.find('blockquote'):
        article.find('blockquote').decompose()
    addict["texte"] = article.getText().replace("\n", " ").replace("\xa0", " ")

    #Récupération de l'url
    addict["url"] = url
    
    #Récupération de la date
    date = page.find("time", {"class" : "dt-published"}).getText()
    addict["date_parution"] = date
    
    
    #Récupération de l'auteur
    author = page.find("a",{"rel":"author"}).getText()
    addict["auteur"] = author
    
    #Inchangés
    addict["journal"] = "ActuGaming"
    addict["tags"] = "gaming"
    return addict

def get_articles(dao=None, nb_articles=100, exclude=None, journal="ActuGaming", gecko_driver_path=None, verbose = 0):
    """Charge tous articles, les sauvegarde en BDD si dao est renseigné

    Args:
        dao (_type_): _description_
        nb_articles (int, optional): _description_. Defaults to 100.
        exclude (_type_, optional): _description_. Defaults to None.
        journal (str, optional): _description_. Defaults to "ActuGaming".
        verbose (int, optional): log level. Defaults to 0.

    Returns:
        list(dict): Papers and article list
    """
       
    articles_urls_to_scrapt = get_links(nb_articles = nb_articles,verbose=verbose, gecko_driver_path=gecko_driver_path)
    
    
    if verbose:
        print("ActuGaming ==> Début du scrapping des articles")

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
                        print("ActuGaming ==> ERROR : Article non ajouté en BDD --------------------------- !!")    
            except Exception as error:
                print("ActuGaming ==> ERROR : ", error, " --------------------------- !!")
        else:
            excluded += 1
    if verbose:
        print(f"ActuGaming ==> {len(articles)} articles and {excluded} exculded arcticles")
    return articles
# 

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                              TESTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


if __name__ == "__main__":

    liste = []

    for url in get_links("https://www.actugaming.net/actualites/"):
        liste.append(get_article(url))

    print(len(liste))