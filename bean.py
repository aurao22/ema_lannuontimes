
paper_frequencies = {"H":"Hebdomadaire", "Q":"Quotidien", "M":"Mensuel", "T":"Trimestriel", "A":"Annuel"}


class Article():
    """_summary_
    """

    def __init__(self, titre, date_parution, url, auteur, texte, resume=None, categorie=None, journal=None, city=None):
        self.titre = titre
        self.date_parution = date_parution
        self.auteur = auteur
        self.texte = texte
        self.categorie = categorie
        self.journal = journal
        self.url = url
        self.city = city
        self.resume = resume

    
class Journal():
    """_summary_
    """
    
    def __init__(self, nom, frequence, fondateur=None, site=None, articles_page=None):
        self.nom = nom
        self.frequence = frequence
        self.fondateur = fondateur
        self.site = site
        self.articles_page = articles_page

