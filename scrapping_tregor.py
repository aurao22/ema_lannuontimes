from scrapping_util import get_page, get_page_links, save_article_in_bdd


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
        liste_urls = get_page_links(section, liste_urls=liste_urls)
        
    if verbose>1:
        print(len(liste_urls), "URLs found")
    return liste_urls

def get_top_articles_urls_liste(page, verbose=0):
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
    for section in page.findAll('div', {'class': "ac-list-preview-articles ac-list-preview-articles--noborder"}):
        liste_urls = get_page_links(section, liste_urls=liste_urls)
        
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

    # récupérer la liste
    liste_urls =set()

    # traitement de la première partie : les articles à la une
    # <section class="ac-grid-preview-home"
    #   <article
    #       <a 
    #   <ul
    #       <li class="ac-preview-article ac-preview-article-small"
    for section in page.findAll('section', {'class': 'ac-grid-preview-home'}):
        liste_urls = get_page_links(section, liste_urls=liste_urls)
        
    # Traitement de la liste d'articles :
    # <div class="ac-list-preview-articles  "
    # <li class="ac-preview-article ac-preview-article-medium"
        # <a href
    for li in page.findAll('li', {'class': 'ac-preview-article ac-preview-article-medium'}):
        liste_urls = get_page_links(li, liste_urls=liste_urls)

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
    article = {'titre':titre, 'date_parution':date_parution, 'url':url ,'auteur':auteur, 'texte':texte, 'tags':tags, 'journal':journal}
    if verbose:
        print(article)
    return article


def get_url_to_scrapt(verbose = 0):
    """Return the url liste to scrapt

    Args:
        verbose (int, optional): log level. Defaults to 0.

    Returns:
        tuple(Journal, list[Article]): Papers and article list
    """
    base_url = "https://actu.fr/"

    to_request_urls = { "actu"  : ["dernieres-actus"],
                        "categ" : ["societe", "economie", "faits-divers", "politique/election-presidentielle", "societe/coronavirus"]
                        #"top" : ["https://actu.fr/bretagne/top", "https://actu.fr/normandie/top", "https://actu.fr/pays-de-la-loire/top", "https://actu.fr/ile-de-france/top", "https://actu.fr/occitanie/top", "https://actu.fr/nouvelle-aquitaine/top", "https://actu.fr/hauts-de-france/top", "https://actu.fr/grand-est/top"]
                        }

    articles_urls_to_scrapt =set()
    url_type = {}
    
    # Parcours de la liste des URLs
    for type_, urls_list in to_request_urls.items():
        for end_point in urls_list:
            try:
                liste_urls = None
                
                target = base_url
                if target not in end_point:
                    target += "le-tregor/"+end_point
                else:
                    target = end_point
                
                if verbose:
                    print("TREGOR ==> Start processing : ", target)

                page = get_page(target)
                if "categ" in type_:
                    liste_urls = get_categ_articles_urls_liste(page, verbose=verbose)
                elif "actu" in type_:
                    liste_urls = get_actu_articles_urls_liste(page, verbose=verbose)
                elif "top" in type_:
                    liste_urls = get_top_articles_urls_liste(page, verbose=verbose)

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
                    print("TREGOR ==> ----- processing : ", target, " => END => ", len(liste_urls), "URLS indentified")
            except Exception as error:
                print(f"TREGOR ==> ERROR while processing {target}")
                print(error)

    if verbose:
        # A ce stade nous avons la liste des URLs à scrapper normalement
        print("TREGOR ==>", len(articles_urls_to_scrapt), "à traiter au total")
    
    return articles_urls_to_scrapt, url_type


def get_articles(dao=None, nb_articles=100, exclude=None, journal="Le Trégor", verbose = 0):
    """retournes tous articles

    Args:
        exclude
        verbose (int, optional): log level. Defaults to 0.

    Returns:
        list(dict): Papers and article list
    """
    articles_urls_to_scrapt, url_type = get_url_to_scrapt(verbose=verbose)
    
    if verbose:
        print("TREGOR ==> Début du scrapping des articles")

    articles = []
    if exclude is None:
        exclude = []
    excluded = 0
    for url in articles_urls_to_scrapt:

        if url not in exclude:
            tags="Actualité"
            try:
                tags=url_type[url]
            except Exception:
                pass
            try:

                art = get_article(url, tags=tags, journal=journal, verbose=verbose)
                if dao is not None:
                    # Ajout de l'article en BDD
                    added = save_article_in_bdd(dao=dao, journal=journal, art=art, verbose = verbose)
                    if not added:
                        print("TREGOR ==> ERROR : Article non ajouté en BDD --------------------------- !!")    
                articles.append(art)
            except Exception as error:
                print("TREGOR ==> ERROR : ", error, " --------------------------- !!")
        else:
            excluded += 1
    if verbose:
        print(f"TREGOR ==> {len(articles)} articles and {excluded} exculded arcticles")
    return articles
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                              TESTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


if __name__ == "__main__":

    art = get_article(url="https://actu.fr/bretagne/prat_22254/autour-de-lannion-six-mois-pour-restaurer-un-tableau-de-1665_49195449.html")

    art = get_article(url="https://actu.fr/bretagne/locquirec_29133/locquirec-la-vigne-va-fleurir-a-lile-blanche_49195371.html")

    articles = get_articles(verbose=1)
    print("END")

            

