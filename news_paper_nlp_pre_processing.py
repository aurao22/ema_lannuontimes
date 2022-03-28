import re
import unicodedata
import matplotlib.pyplot as plt
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.corpus.reader import WordListCorpusReader
import warnings
warnings.filterwarnings("ignore")
try:
    from sklearn.utils._testing import ignore_warnings
except ImportError:
    from sklearn.utils.testing import ignore_warnings
from sklearn.exceptions import ConvergenceWarning

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


def get_numeric_columns_names(df, verbose=False):
    """Retourne les noms des colonnes numériques
    Args:
        df (DataFrame): Données
        verbose (bool, optional): Mode debug. Defaults to False.

    Returns:
        List(String): liste des noms de colonne
    """
    numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    newdf = df.select_dtypes(include=numerics)
    return list(newdf.columns)

# ----------------------------------------------------------------------------------
#                        MODELS : FIT AND TEST
# ----------------------------------------------------------------------------------
from sklearn.svm import LinearSVC
import time

def fit_and_test_models(model_list, X_train, Y_train, X_test, Y_test, y_column_name=None, verbose=0, scores=None, metrics=0, transformer=None):
    
    # Sauvegarde des modèles entrainés
    modeldic = {}
    yt = Y_test
    ya = Y_train
    # Sauvegarde des données
    if scores is None:
        scores = defaultdict(list)

    if y_column_name is None:
        y_column_name = ""
    else:
        yt = Y_test[y_column_name]
        ya = Y_train[y_column_name]

    scorelist = []
    try:
        for mod_name, model in model_list.items():
            try:
                model_name = mod_name
                if len(y_column_name) > 0:
                    model_name = y_column_name+"-"+model_name

                if isinstance(model, LinearSVC):
                    if ya.nunique() <= 2:
                        continue
                scores["Class"].append(y_column_name)
                scores["Model"].append(mod_name)
                md, score_l = fit_and_test_a_model(model,model_name, X_train, ya, X_test, yt, verbose=verbose, metrics=metrics, transformer=transformer) 
                modeldic[model_name] = md
                scorelist.append(score_l)
            except Exception as ex:
                print(mod_name, "FAILED : ", ex)
        
        for score_l in scorelist:
            for key, val in score_l.items():
                scores[key].append(val)    
    except Exception as ex:
            print(mod_name, "FAILED : ", ex)

    return modeldic, scores

@ignore_warnings(category=ConvergenceWarning)
def fit_and_test_a_model(model, model_name, X_train, y_train, X_test, y_test, verbose=0, metrics=0, transformer=None):
    t0 = time.time()
    if verbose:
        print(model_name, "X_train:", X_train.shape,"y_train:", y_train.shape, "X_test:", X_test.shape,"y_test:", y_test.shape)

    if transformer is not None:
        try:
            X_train = transformer.fit_transform(X_train)
            X_test = transformer.fit_transform(X_test)
            if verbose:
                print(model_name, "After transform : X_train:", X_train.shape,"y_train:", y_train.shape, "X_test:", X_test.shape,"y_test:", y_test.shape)
        except:
            pass
    model.fit(X_train, y_train)
    
    r2 = model.score(X_test, y_test)
    if verbose:
        print(model_name+" "*(20-len(model_name))+":", round(r2, 3))
    t_model = (time.time() - t0)
        
    # Sauvegarde des scores
    modeldic_score = {"Modeli":model_name,
                      "R2":r2,
                      "fit time":time.strftime("%H:%M:%S", time.gmtime(t_model)),
                      "fit seconde":t_model}
    
    # Calcul et Sauvegarde des métriques
    if metrics > 0:
        full=metrics > 1
        t0 = time.time()
        model_metrics = get_metrics_for_the_model(model, X_test, y_test, y_pred=None,scores=None, model_name=model_name, r2=r2, full_metrics=full, verbose=verbose, transformer=transformer)
        t_model = (time.time() - t0)   
        modeldic_score["metrics time"] = time.strftime("%H:%M:%S", time.gmtime(t_model))
        modeldic_score["metrics seconde"] = t_model

        for key, val in model_metrics.items():
            if "R2" not in key and "Model" not in key:
                modeldic_score[key] = val[0]

    return model, modeldic_score


from sklearn.metrics import *
from sklearn.metrics import roc_curve, RocCurveDisplay, precision_recall_curve, PrecisionRecallDisplay

from collections import defaultdict
import pandas as pd

# ----------------------------------------------------------------------------------
#                        MODELS : METRICS
# ----------------------------------------------------------------------------------
def get_metrics_for_the_model(model, X_test, y_test, y_pred,scores=None, model_name="", r2=None, verbose=0):
    if scores is None:
        scores = defaultdict(list)
    scores["Model"].append(model_name)
        
    if r2 is None:
        r2 = round(model.score(X_test, y_test),3)
        
    if y_pred is None:
        t0 = time.time()
        y_pred = model.predict(X_test)
        t_model = (time.time() - t0)   
        # Sauvegarde des scores
        scores["predict time"].append(time.strftime("%H:%M:%S", time.gmtime(t_model)))
        scores["predict seconde"].append(t_model)
        
    scores["R2"].append(r2)
    scores["MAE"].append(mean_absolute_error(y_test, y_pred))
    mse = mean_squared_error(y_test, y_pred)
    scores["MSE"].append(mse)
    scores["RMSE"].append(np.sqrt(mse))
    scores["Mediane AE"].append(median_absolute_error(y_test, y_pred))

    return scores

def get_metrics_for_model(model_dic, X_test, y_test, verbose=0):
    score_df = None
    scores = defaultdict(list)
    for model_name, (model, y_pred, r2) in model_dic.items():
        scores = get_metrics_for_the_model(model, X_test, y_test, y_pred, scores,model_name=model_name, r2=r2, verbose=verbose)

    score_df = pd.DataFrame(scores).set_index("Model")
    score_df.round(decimals=3)
    return score_df

from joblib import dump, load
from datetime import datetime

def save_model(model_to_save, file_path):
    # Sauvegarde du meilleur modele
    now = datetime.now() # current date and time
    date_time = now.strftime("%Y-%m-%d-%H_%M_%S")
    model_save_file_name = 'ema_lannuontimes_saved_model_' + date_time + '.joblib'
    # Attention, il faudra mettre à jour les colonnes correspondantes dans le premier if en cas de modification du model
    dump(model_to_save, file_path)

from os import path
def load_model(model_save_path):
    if path.exists(model_save_path) and path.isfile(model_save_path):
        # Chargement du modèle pré-entrainer
        return load(model_save_path)


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


from wordcloud import WordCloud

def word_cloud(journal, df_articles):
    text_ag = ''.join(df_articles[df_articles["journal"]==journal]["texte_clean"].tolist())
    word_cloud = WordCloud(collocations = False, background_color = 'white').generate(text_ag)
    
    plt.rcParams["figure.figsize"]=(15, 8)
    plt.imshow(word_cloud, interpolation='bilinear')
    plt.title(journal.upper(), fontsize=16)
    plt.axis("off")
    plt.show()