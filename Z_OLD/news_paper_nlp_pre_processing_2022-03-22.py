import re
import unicodedata
import matplotlib.pyplot as plt
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.corpus.reader import WordListCorpusReader

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                              FUNCTIONS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Regex

def get_regex_urls(verbose=0):
    # Version moins performante :
    # pattern = r'https?://\S+|www\.\S+'
    pattern = re.compile(r'http.+?(?=\?|"|<)')
    return pattern

def get_regex_tokens(verbose=0):
    pattern = re.compile(r"\b\w+\b")
    return pattern

def get_regex_alphabetique_simple(verbose=0):
    pattern = re.compile(r'[^a-zA-Z]')
    return pattern

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TOKENIZATION functions

def tokenize(text, use_reg=True, use_nlk=False, verbose=0):
    res = None

    if isinstance(text, str):
        if use_reg:
            res = re.findall(get_regex_tokens(), text.lower())
        if use_nlk:
            res = word_tokenize(text.lower())

    elif isinstance(text, list):
        res = [tokenize(sentence,use_reg=use_reg, use_nlk=use_nlk, verbose=verbose)  for sentence in text]
        res = list(filter(None, res))

    return res

def df_word_tokenize(df, text_col_name, token_col_name="word_tokenize", use_reg=True, use_nlk=False, verbose=0):
    df_token = df.copy()

    df_token[token_col_name] = df_token[text_col_name].apply(lambda x: tokenize(x, use_reg=use_reg, use_nlk=use_nlk, verbose=verbose))
    return df_token

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Evaluating functions
def word_count_func(text):
    '''
    Counts words within a string
    
    Args: text (str or list[str] ): String to which the function is to be applied, string
    Returns: Number of words within a string, integer
    ''' 
    if isinstance(text, str):
        return len(text.split())
    elif isinstance(text, list):
        return word_count_func(' '.join(text))
    return len(text.split())


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Cleanning function

def remove_irr_char_func(text):
    '''
    Removes all irrelevant characters (numbers and punctuation) from a string, if present
    
    Args: text (str): String to which the function is to be applied, string
    Returns: Clean string without irrelevant characters
    '''
    if isinstance(text, str):
        return re.sub(get_regex_alphabetique_simple(), ' ', text).strip()
    elif isinstance(text, list):
        res = []
        for s in text:
            res.append(remove_irr_char_func(s))
        res = list(filter(None, res))
        return res

def remove_url_func(text):
    '''
    Removes URL addresses from a string, if present
    Args: text (str): String to which the function is to be applied, string
    Returns: Clean string without URL addresses
    ''' 
    pattern = get_regex_urls()
    return re.sub(pattern, '', text)

def normalize_accented_chars(text):
    '''
    Removes all accented characters from a string, if present
    Args: text (str): String to which the function is to be applied, string
            ex: Hello, is your name bob 55? Jean-Marie est 3ème ! Est-ce que tu l'as vu aujourd'hui ?é où à î @ # &
            > Hello, is your name bob 55? Jean-Marie est 3eme ! Est-ce que tu l'as vu aujourd'hui ?e ou a i @ # &
    Returns: Clean string without accented characters
    '''
    if isinstance(text, str):
        return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8', 'ignore').strip()
    elif isinstance(text, list):
        res = []
        for s in text:
            res.append(normalize_accented_chars(s))
        res = list(filter(None, res))
        return res

def remove_stopwords_func(text, language="french", sw=None):
    '''
    Removes Stop Words (also capitalized) from a string, if present
    
    Args:
        text (str or list): String to which the function is to be applied, string
        language (str, optionnal) : french, english, ... default : french
    Returns: Clean (str or list) without Stop Words
    ''' 
    res = None
    # check in lowercase 
    if isinstance(text, str):
        res_list = remove_stopwords_func(text.split(" "), language=language, sw=sw)
        text = ' '.join(res_list)    
        res = text
    elif isinstance(text, list):
        if sw is None :
            sw = list(stopwords.words(language))
        if isinstance(sw, WordListCorpusReader):
            sw = sw.words()
        
        res = []
        for sentence in text:
            token_temp = sentence.split()
            t = [token.strip() for token in token_temp if token.lower() not in sw]
            res.append(' '.join(t))
        res = list(filter(None, res))
    return res

# ----------------------------------------------------------------------------------
#                        GRAPHIQUES
# ----------------------------------------------------------------------------------
PLOT_FIGURE_BAGROUNG_COLOR = 'white'
PLOT_BAGROUNG_COLOR = PLOT_FIGURE_BAGROUNG_COLOR


def color_graph_background(ligne=1, colonne=1):
    figure, axes = plt.subplots(ligne,colonne)
    figure.patch.set_facecolor(PLOT_FIGURE_BAGROUNG_COLOR)
    if isinstance(axes, np.ndarray):
        for axe in axes:
            # Traitement des figures avec plusieurs lignes
            if isinstance(axe, np.ndarray):
                for ae in axe:
                    ae.set_facecolor(PLOT_BAGROUNG_COLOR)
            else:
                axe.set_facecolor(PLOT_BAGROUNG_COLOR)
    else:
        axes.set_facecolor(PLOT_BAGROUNG_COLOR)
    return figure, axes