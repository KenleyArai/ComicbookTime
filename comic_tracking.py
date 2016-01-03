
# coding: utf-8

# In[131]:

import re
import shutil
import os.path

import requests as rq
import pandas as pd

from sqlalchemy.sql import select
from datetime import datetime
from bs4 import BeautifulSoup as bs
from fuzzywuzzy import process
from models import Comics, Series
from database import engine, db_session
from operator import itemgetter
from time import sleep

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
            new_series = Series(name=title, comic_child=[comic_child])

            db_session.add(new_series)
            db_session.commit()
        else:
            options = process.extract(title, result)
            maximum = max(options, key=itemgetter(1))

            if maximum[1] < 85:
                comic_child = db_session.query(Comics).filter_by(title=data['title'])[0]
                new_series = Series(name=title, comic_child=[comic_child])

                db_session.add(new_series)
                db_session.commit()
            else:
                comic_child = db_session.query(Comics).filter_by(title=data['title'])[0]
                series = db_session.query(Series).filter_by(name=title)[0]
                comic_child.seriesID = series.id

                db_session.commit()


def download_kimage(url, comic_id):
    if not url or "no-image" in url:
        return None
    r = rq.get(url, stream=True)
    if r.status_code != 200:
        sleep(30)
        r = rq.get(url, stream=True)
    path = "".join(['static/covers/', str(comic_id), '.png'])

    with open(path, 'wb') as out_file:
        shutil.copyfileobj(r.raw, out_file)


def get_image(url):
    image_url = None

    r = rq.get(url)
    soup = bs(r.text, 'html.parser')

    if "gocollect" in url:
        image_url = soup.find('img', {'class':'shadow-1'})
        image_url = image_url['src']
        if image_url == "/images/no-item-image.png":
            image_url = None

    return image_url


def get_marvel_dataframe(url):
    marvel = []
    headers = ["url", "title", "notes", "release_date", "image_link", "availability"]
    comics = pd.DataFrame(columns=headers)

    r = rq.get(url)
    soup = bs(r.text, 'html.parser')

    paras = soup.findAll('p')
    # Finding the date they are supposed to be listed
    match = re.search(r'(\d{2}/\d{2}/\d{4})', soup.h1.string)
    date = datetime.strptime(match.group(), '%m/%d/%Y').date()
    availability = date < datetime.date(datetime.now())

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

                if not result:
                    new_row = []
                    new_row.append(a['href'])
                    new_row.append(title[0])
                    new_row.append(title[1])
                    new_row.append(date)
                    new_row.append(get_image(a['href']))
                    new_row.append(availability)
                    comics.loc[len(comics)] = new_row

    return comics

def update_marvel_database(urls):
    frames = []

    for url in urls:
        frames += [get_marvel_dataframe(url)]

    without_dups = pd.concat(frames)
    without_dups.drop_duplicates(['title'], inplace=True)
    update_db(without_dups, TABLE)

def update_db(dataframe, table):
    e = engine

    if len(dataframe) != 0:
        dataframe.to_sql(name=table, con=e, if_exists="append", index=False)

        for index, row in dataframe.iterrows():
            s = select([Comics.id]).where(Comics.title == row['title'])
            result = db_session.execute(s).fetchone()[0]

            download_image(row['image_link'], result)

        update_series(dataframe)
