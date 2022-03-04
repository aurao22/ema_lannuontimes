from urllib import request
import bs4
import collections
import numpy as np
import pandas as pd
from datetime import datetime
from os import getcwd
from PIL import Image
import re


def get_page(url):
    req = request.Request(url, headers = {'User-Agent' : 'Mozilla/5.0'})
    html = request.urlopen(req).read()
    return bs4.BeautifulSoup(html, "lxml")