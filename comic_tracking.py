
# coding: utf-8

# In[131]:

import re
import sqlite3

import requests as rq
import pandas as pd

from datetime import datetime
from bs4 import BeautifulSoup as bs

from database import engine

DATABASE = "./comics.db"
TABLE = "comics"


# In[115]:

def get_marvel_dataframe(url):
    marvel = []
    urls = []
    titles = []
    comics = pd.DataFrame()

    r = rq.get(url)
    soup = bs(r.text, 'html.parser')

    paras = soup.findAll('p')
    # Finding the date they are supposed to be listed
    match = re.search(r'(\d{2}/\d{2}/\d{4})', soup.h1.string)
    date = datetime.strptime(match.group(), '%m/%d/%Y').date()
    
    # Searching through each paragraph tag for the Marvel header
    for paragraph in paras:
        if paragraph.b and "MARVEL COMICS" == paragraph.b.u.string:
            marvel = paragraph        

    print(marvel)
    for a in marvel.findAll('a'):
        urls   += [a['href']]
        titles += [a.string]

    comics['url'] = pd.Series(urls)
    comics['title'] = pd.Series(titles)
    comics['release_date'] = pd.Series([date for _ in urls])
    
    return comics


def update_marvel_database(urls):
    frames = []

    for url in urls:
        frames += [get_marvel_dataframe(url)] 

    without_dups = pd.concat(frames)
    update_db(DATABASE, without_dups, TABLE)

def update_db(database, dataframe, table):
    e = engine
    dataframe.to_sql(name=table, con=e, if_exists="append", index=False)
