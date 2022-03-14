from black import err
from scrapping_util import get_page, get_page_links, save_article_in_bdd

def get_div_text(balise, verbose=0):

    lignes = []
    if balise is not None:
        for child in balise.findChildren():
            if "p" == child.name or "h2" == child.name:
                if "pageliste" in child.get("class"):
                    # On sort de la boucle car nous sommes à la fin de l'article
                    break
                ligne = child.get_text().strip()
                if ligne.startswith(">> Partagez cette actu sur") or ligne.startswith("Abonnez-vous") or ligne.startswith("à lire aussi"):
                    # Fin de l'article
                    break
                else:
                    lignes.append(ligne)
                    if verbose>1:
                        print(ligne)
            elif "div" == child.name:
                lignes.extend(get_div_text(child, verbose=verbose))
    return lignes


def get_article(url, journal=None, verbose=0):
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
    page = page.find('body')
    
    # balise titre : <h1></h1>
    titre = page.find('h1').get_text().strip()
    if titre is None or len(titre.strip())==0:
        try:
            titre = page.find('div', {'class': 'surcontent'}).find('h1').get_text().strip()
        except Exception as error:
            print(error)
    date_parution = page.find('span', {'class': 'date'}).get_text().strip()
    auteur = ""
    texte = ""

    tags = page.find('span', {'class': 'cat'}).get_text().strip()

    art = page.find('div', {'class': 'tt-news'})
    if art is not None:
        art = art.find("div", {'class': 'news-single-item'}) if art.find("div", {'class': 'news-single-item'}) is not None else art
        
        lignes = []
        # On parcours les balises enfant et on garde uniquement les 
        # <p>
        # <h2>
        for child in art.findChildren():
            if "div" == child.name and "ac-article-tag" == child.get("class"):
                # p class="bodytext"
                if tags is None:
                    tags = ""
                for tag in child.findAll('a'):
                    tags += "," + tag.get_text().strip().replace("#", "")
                # On sort de la boucle car on est à la fin de l'article
                break
            else:
                try:
                    if child.get("class") is not None and "pageliste" in child.get("class"):
                        # On sort de la boucle car nous sommes à la fin de l'article
                        break
                    if "p" == child.name and child.get("class") is not None and "news-single-imgcaption" in child.get("class"):
                        pass
                    else:
                        ligne = child.get_text().strip()
                        if ligne.startswith("Cet article vous a été utile"):
                            # Fin de l'article
                            break
                        elif ligne.startswith("À lire aussi") or ligne.startswith(">> Partagez cette actu sur Facebook"):
                            pass
                        else:
                            lignes.append(ligne)
                            if verbose>1:
                                print(ligne)
                except Exception as error:
                    print(error)

    texte = " ".join(lignes)
    article = {'titre':titre, 'date_parution':date_parution, 'url':url ,'auteur':auteur, 'texte':texte.strip(), 'tags':tags, 'journal':journal}
    if verbose:
        print(article)
    return article


def get_url_to_scrapt(nb_articles=100, verbose = 0):
    """Return the url liste to scrapt

    Args:
        verbose (int, optional): log level. Defaults to 0.

    Returns:
        tuple(Journal, list[Article]): Papers and article list
    """
    base_url = "https://www.30millionsdamis.fr/"
    page_url = base_url+"actualites/actu-page/1/"
    
    nb_page_to_proceed = nb_articles // 16

    liste_urls =set()
        
    for i in range(0, nb_page_to_proceed):
        target = page_url.replace("1", str(i))
        if i == 0:
            target = base_url + "actualites/"

        try:
            if verbose:
                print("30 M. d'AMIS ==> Start processing : ", target)

            page = get_page(target)
            for section in page.findAll('div', {'class': "tt-news"}):
                before = len(liste_urls)

                liste_urls = get_page_links(section, base_url=base_url, liste_urls=liste_urls, verbose=verbose)
                temp = liste_urls.copy()
                for u in temp:
                    if "article" not in u:
                        liste_urls.remove(u)

                if verbose:
                    print("30 M. d'AMIS ==> ----- processing : ", target, " => END => ", len(liste_urls)-before, " URLS indentified")
        except Exception as error:
            print(f"30 M. d'AMIS ==> ERROR while processing {target}")
            print(error)

    if verbose:
        # A ce stade nous avons la liste des URLs à scrapper normalement
        print("30 M. d'AMIS ==>", len(liste_urls), "à traiter au total")
    
    return liste_urls


def get_articles(dao=None, nb_articles=100, exclude=None, journal="30 M. d'amis", verbose = 0):
    """Charge tous articles, les sauvegarde en BDD si dao est renseigné

    Args:
        dao (_type_): _description_
        nb_articles (int, optional): _description_. Defaults to 100.
        exclude (_type_, optional): _description_. Defaults to None.
        journal (str, optional): _description_. Defaults to "30 M. d'amis".
        verbose (int, optional): log level. Defaults to 0.

    Returns:
        list(dict): Papers and article list
    """
       
    articles_urls_to_scrapt = get_url_to_scrapt(nb_articles = nb_articles,verbose=verbose)
    
    if verbose:
        print("30 M. d'AMIS ==> Début du scrapping des articles")

    articles = []
    if exclude is None:
        exclude = []
    excluded = 0
    for url in articles_urls_to_scrapt:
        if url not in exclude:
            try:

                art = get_article(url,journal=journal, verbose=verbose)
                articles.append(art)

                if dao is not None:
                    # Ajout de l'article en BDD
                    added = save_article_in_bdd(dao=dao, journal=journal, art=art, verbose = verbose)
                    if not added:
                        print("30 M. d'AMIS ==> ERROR : Article non ajouté en BDD --------------------------- !!")    
                articles.append(art)
            except Exception as error:
                print("30 M. d'AMIS ==> ERROR : ", error, " --------------------------- !!")
        else:
            excluded += 1
    if verbose:
        print(f"30 M. d'AMIS ==> {len(articles)} articles and {excluded} exculded arcticles")
    return articles
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                              TESTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


if __name__ == "__main__":

    verbose = 1
    articles_urls_to_scrapt = list(get_url_to_scrapt(nb_articles=50, verbose=1))

    assert articles_urls_to_scrapt

    link = "/actualites/article/21831-un-malinois-squelettique-secouru-par-la-fondation-30-millions-damis/"
    base_url = "https://www.30millionsdamis.fr/actualites/"
    print(articles_urls_to_scrapt[0])
    art = get_article(url=articles_urls_to_scrapt[0], verbose=verbose)

    assert art

    articles = get_articles(nb_articles=50,verbose=1)
    print("END")

            

