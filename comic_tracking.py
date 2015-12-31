
# coding: utf-8

# In[131]:

import re
import sqlite3

import sqlalchemy

import requests as rq
import pandas as pd

from sqlalchemy.sql import select
from datetime import datetime
from bs4 import BeautifulSoup as bs
from fuzzywuzzy import process
from models import Comics, Series 
from database import engine, db_session
from operator import itemgetter

DATABASE = "./comics.db"
TABLE = "comics"


# In[115]:

def update_series(df):
    for index, data in df.iterrows():
        title = data['title'][:-3]
        columns = [Series.name]
        mask = "".join(["%", title,"%"])
        mask = Series.name.like(mask)
        s = select(columns).where(mask)
        result = [x[0] for x in db_session.execute(s).fetchall()]

        if not result:
            comic_child = db_session.query(Comics).filter_by(title=data['title'])[0]
            new_series = Series(name=title, comic_child=[child_comic])

            db_session.add(new_series)
            db_session.commit()
        else:
            options = process.extract(title, result)
            maximum = max(options, key=itemgetter(1))

            comic_child = db_session.query(Comics).filter_by(title=data['title'])[0]
            series = db_session.query(Series).filter_by(name=title)[0]
            comic_child.seriesID = series.id

            db_session.commit()
            

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

                s = select([Comics.title]).where(Comics.title == title[0])
                 
                result = db_session.execute(s).fetchone()

                #if not result: 
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

    if len(dataframe) != 0:
        dataframe.to_sql(name=table, con=e, if_exists="append", index=False)
        update_series(dataframe)
