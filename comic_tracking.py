
# coding: utf-8

# In[131]:

import re
import sqlite3

import requests as rq
import pandas as pd

import sqlalchemy
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
    notes = []
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

    for a in marvel.findAll('a'):
        if "Variant" not in a.string: 
            title = a.string.split("#")
            if len(title) > 1:
                title[0] = title[0] + "#" + title[1][0]
                title[1] = title[1][1:]

                urls   += [a['href']]
                titles += [title[0]]
                notes += [title[1]]

    comics['url'] = pd.Series(urls)
    comics['title'] = pd.Series(titles)
    comics['release_date'] = pd.Series([date for _ in urls])
    comics['notes'] = pd.Series(notes)

    return comics


def update_marvel_database(urls):
    frames = []

    for url in urls:
        frames += [get_marvel_dataframe(url)] 

    without_dups = pd.concat(frames)
    update_db(DATABASE, without_dups, TABLE)

def update_db(database, dataframe, table):
    e = engine
    df = pd.read_sql("comics", con=e)
    new_df = pd.concat([df, dataframe])
    new_df.drop_duplicates(subset=['title','release_date'], inplace=True)
    new_df.to_sql(name=table, con=e, if_exists="replace", index=False)
