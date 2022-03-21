from scrapping_util import get_page, get_selenium_firefox_driver, save_article_in_bdd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
import time
import math

def get_links(url, nb_articles=20, verbose=0):
    DRIVER_PATH = 'geckodriver.exe'
    # driver = webdriver.Firefox(service=Service(DRIVER_PATH))
    # driver.get(url)
    # time.sleep(5)
    driver = get_selenium_firefox_driver(url, gecko_driver_path=DRIVER_PATH)
    refuse_btn = driver.find_element(by=By.CLASS_NAME, value='css-1g6dv8a')
    refuse_btn.click()
    load_more_btn = driver.find_element(by=By.CLASS_NAME, value='alm-load-more-btn')
    load_times = math.ceil((nb_articles - 12) / 8)
    for i in range(load_times):
        time.sleep(5)

        load_more_btn.click()
        

    time.sleep(5)
    elems = driver.find_elements(by=By.XPATH, value="//figure/a[@href]")
    urls = []
    for elem in elems[:nb_articles]:
        urls.append(elem.get_attribute("href"))

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

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                              TESTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


if __name__ == "__main__":

    liste = []

    for url in get_links("https://www.actugaming.net/actualites/"):
        liste.append(get_article(url))

    print(len(liste))