from urllib import request
import bs4


def get_page(url, verbose=0):
    """Retrieve the HTML page

    Args:
        url (str): the page URL
        verbose (int, optional): Log level. Defaults to 0.

    Returns:
        BeautifulSoup: the page
    """
    if verbose>1:
        print("Request url :", url)
    req = request.Request(url, headers = {'User-Agent' : 'Mozilla/5.0'})
    html = request.urlopen(req).read()
    return bs4.BeautifulSoup(html, "lxml")