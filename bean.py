
paper_frequencies = {"H":"Hebdomadaire", "Q":"Quotidien", "M":"Mensuel", "T":"Trimestriel", "A":"Annuel"}


class Article():
    """_summary_
    """

    def __init__(self, titre, date_parution, url, auteur, texte, resume=None, journal=None, tags=None):
        self.titre = titre
        self.date_parution = date_parution
        self.auteur = auteur
        self.texte = texte
        self.journal = journal
        self.url = url
        self.tags = tags
        self.resume = resume

    def __str__(self):
        journal_name = "None"
        if self.journal is not None:
            journal_name = self.journal.nom
        return f"{journal_name} - {self.titre} du {self.date_parution}, de {self.auteur}, TAGS : {self.tags}, {self.resume}"
    

    
class Journal():
    """_summary_
    """
    
    def __init__(self, nom, frequence, fondateur=None, site=None, articles_page=None):
        self.nom = nom
        self.frequence = frequence
        self.fondateur = fondateur
        self.site = site
        self.articles_page = articles_page

