from urllib import request
import bs4
import collections
import numpy as np
import pandas as pd
from datetime import datetime
from os import getcwd
import re

from scrapping_util import *


base_url = "https://actu.fr/le-tregor/"

to_request_urls = { "actu"  : ["dernieres-actus"],
                    "categ" : ["loisirs-culture", "societe", "economie", "faits-divers", "politique/election-presidentielle", "societe/coronavirus"]
                    }

verbose = 1

def get_actu_articles_urls_liste(page, verbose=0):
    """Search all article URLs in the page

    Args:
        page (BeautifulSoup): _description_
        verbose (int, optional): log level. Defaults to 0.

    Raises:
        AttributeError: if page is missing

    Returns:
        list(str): list of Articles page URL
    """
    if page is None:
        raise AttributeError("page expected")

    # récupérer la liste des noms de pokémon
    liste_urls =set()

    # traitement de la première partie : les articles à la une
    # <article class="ac-preview-article ac-preview-last-news"> <a href
    for section in page.findAll('article', {'class': 'ac-preview-article ac-preview-last-news'}):
        for lien in section.findAll('a'):
            liste_urls.add(lien.get('href'))

    if verbose:
        print(len(liste_urls), "URLs found")
    return liste_urls


def get_categ_articles_urls_liste(page, verbose=0):
    """Search all article URLs in the page

    Args:
        page (BeautifulSoup): _description_
        verbose (int, optional): log level. Defaults to 0.

    Raises:
        AttributeError: if page is missing

    Returns:
        list(str): list of Articles page URL
    """
    if page is None:
        raise AttributeError("page expected")

    # récupérer la liste des noms de pokémon
    liste_urls =set()

    # traitement de la première partie : les articles à la une
    # <section class="ac-grid-preview-home"
    #   <article
    #       <a 
    #   <ul
    #       <li class="ac-preview-article ac-preview-article-small"
    for section in page.findAll('section', {'class': 'ac-grid-preview-home'}):
        for a in section.findAll('a'):
            lien = a.get('href')
            liste_urls.add(lien)

    # Traitement de la liste d'articles :
    # <div class="ac-list-preview-articles  "
    # <li class="ac-preview-article ac-preview-article-medium"
        # <a href
    for li in page.findAll('li', {'class': 'ac-preview-article ac-preview-article-medium'}):
        lien = li.find('a').get('href')
        liste_urls.add(lien)

    if verbose:
        print(len(liste_urls), "URLs found")
    return liste_urls


def get_article(url, tags=None, journal=None, verbose=0):
    if url is None or len(url)==0:
        raise AttributeError("URL expected")

    page = get_page(url)

    titre = ""
    date_parution = ""
    auteur = ""
    texte = ""
    # TODO scrapping

    # article exemple : https://actu.fr/bretagne/lannion_22113/lannion-orange-renove-un-batiment-pour-en-faire-un-centre-de-test-mondial_49150955.html
    # <article class="js-article-inner">
    art = page.find('article', {'class': 'js-article-inner'})
    if art is not None:
        # balise titre : <h1></h1>
        titre = art.find('h1').get_text().strip()
        
        # DATE : <div class="ac-article-date">
        parution = art.find('div', {'class': 'ac-article-date'}).get_text().strip()
        'Par Christophe Ganne\nPublié le 3 Mar 22 à 17:29'
        parutions = parution.split("\nPublié le ")
        if 'Par ' in parutions[0]:
            auteur = parutions[0].replace('Par ', "")
            if len(parutions)>1:
                date_parution = parutions[1].split("\n")[0]
        else:
            date_parution = parutions[0].split("\n")[0]
        date_parution = date_parution.strip()
        # Libération des variables
        parution=None
        parutions = None
        
        # resume : <p> </p>
        resume = art.find('p').get_text().strip()
        lignes = []
        # traitement du texte de l'article :
        content_balise = art.find('div', {'class': 'ac-article-content'})

        # On parcours les balises enfant et on garde uniquement les 
        # <p>
        # <h2>
        for child in content_balise.findChildren():
            if "p" == child.name or "h2" == child.name:
                lignes.append(child.get_text().strip())

    texte = " ".join(lignes)
                    # titre, date_parution, url, auteur, texte, resume=None, journal=None, tags=None
    article = Article(titre=titre, date_parution=date_parution, url=url ,auteur=auteur, texte=texte, tags=tags, resume=resume, journal=journal)
    return article


articles_urls_to_scrapt =set()
url_type = {}

# Parcours de la liste des URLs
for type_, urls_list in to_request_urls.items():
    for end_point in urls_list:
        liste_urls = None
        if verbose:
            print("Start processing : ", base_url+end_point)
        page = get_page(base_url+end_point)
        if "categ" in type_:
            liste_urls = get_categ_articles_urls_liste(page, verbose=verbose)
        elif "actu" in type_:
            liste_urls = get_actu_articles_urls_liste(page, verbose=verbose)

        if liste_urls is not None and len(liste_urls) > 0:
            if "categ" in type_:
                for url in liste_urls:
                    url_type[url] = end_point

            if articles_urls_to_scrapt is None or len(articles_urls_to_scrapt) == 0:
                articles_urls_to_scrapt = liste_urls
            else:
                if verbose:
                    print(len(articles_urls_to_scrapt), "plus", len(liste_urls), "=", end="")
                articles_urls_to_scrapt.union(articles_urls_to_scrapt, liste_urls) 
                if verbose:
                    print(len(articles_urls_to_scrapt))

        if verbose:
            print("----- processing : ", base_url+end_point, " => END => ", len(liste_urls), "URLS indentified")

# A ce stade nous avons la liste des URLs à scrapper normalement
print(len(articles_urls_to_scrapt), "à traiter au total")

# TODO récupérer le texte des articles
from bean import *

tregor = Journal("Le Trégor", "H", fondateur="", site=base_url, articles_page=base_url+"dernieres-actus")

articles = []

for url in articles_urls_to_scrapt:
    tags="Actualité"
    try:
        tags=url_type[url]
    except Exception:
        pass
    try:
        art = get_article(url, tags=tags, journal=tregor, verbose=verbose)
    except Exception as error:
        print("ERROR : ", error)


            

