from bean import *
from scrapping_util import *


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

    if verbose>1:
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

    if verbose>1:
        print("TREGOR ==>", len(liste_urls), "URLs found")
    return liste_urls


def get_article(url, tags=None, journal=None, verbose=0):
    """Retrieve article data

    Args:
        url (str): the article page url
        tags (str, optional): the tags. Defaults to None.
        journal (Journal, optional): The paper. Defaults to None.
        verbose (int, optional): log level. Defaults to 0.

    Raises:
        AttributeError: if url is missing

    Returns:
        Article: the article
    """
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
                ligne = child.get_text().strip()
                if ligne.startswith("Cet article vous a été utile"):
                    # Fin de l'article
                    break
                elif ligne.startswith("À lire aussi"):
                    pass
                else:
                    lignes.append(ligne)
                    if verbose>1:
                        print(ligne)
            elif "div" == child.name and "ac-article-tag" == child.get("class"):
                if tags is None:
                    tags = ""
                for tag in child.findAll('a'):
                    tags += "," + tag.get_text().strip().replace("#", "")
                # On sort de la boucle car on est à la fin de l'article
                break

    texte = " ".join(lignes)
    article = Article(titre=titre, date_parution=date_parution, url=url ,auteur=auteur, texte=texte, tags=tags, resume=resume, journal=journal)
    if verbose:
        print(article)
    return article


def load_articles(verbose = 0):
    """Load all papers articles

    Args:
        verbose (int, optional): log level. Defaults to 0.

    Returns:
        tuple(Journal, list[Article]): Papers and article list
    """
    
    base_url = "https://actu.fr/le-tregor/"

    to_request_urls = { "actu"  : ["dernieres-actus"],
                        "categ" : ["loisirs-culture", "societe", "economie", "faits-divers", "politique/election-presidentielle", "societe/coronavirus"]
                        }

    articles_urls_to_scrapt =set()
    url_type = {}

    # Parcours de la liste des URLs
    for type_, urls_list in to_request_urls.items():
        for end_point in urls_list:
            liste_urls = None
            if verbose:
                print("TREGOR ==> Start processing : ", base_url+end_point)
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
                        print("TREGOR ==>", len(articles_urls_to_scrapt), "plus", len(liste_urls), "=", end="")
                    articles_urls_to_scrapt.union(articles_urls_to_scrapt, liste_urls) 
                    if verbose:
                        print("TREGOR ==>", len(articles_urls_to_scrapt))

            if verbose:
                print("TREGOR ==> ----- processing : ", base_url+end_point, " => END => ", len(liste_urls), "URLS indentified")

    if verbose:
        # A ce stade nous avons la liste des URLs à scrapper normalement
        print("TREGOR ==>", len(articles_urls_to_scrapt), "à traiter au total")
        print("TREGOR ==> Début du scrapping des articles")

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
            articles.append(art)
        except Exception as error:
            print("TREGOR ==> ERROR : ", error, " --------------------------- !!")
    if verbose:
        print("TREGOR ==>", len(articles), "articles chargés")
    return tregor, articles

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                              TESTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


if __name__ == "__main__":
    tregor, articles = load_articles(verbose=1)
    print("END")

            

