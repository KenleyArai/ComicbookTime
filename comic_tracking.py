
# coding: utf-8

# In[131]:

import re
import shutil
import os.path

import requests as rq
import pandas as pd

from sqlalchemy import Column, Boolean
from sqlalchemy.sql import select
from datetime import datetime
from dateutil.relativedelta import relativedelta
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

        comic_child = db_session.query(Comics).filter_by(title=data['title']).one()
        if not result:
            new_series = Series(name=title, comic_child=[comic_child])
            db_session.add(new_series)
        else:
            options = process.extract(title, result)
            maximum = max(options, key=itemgetter(1))

            if maximum[1] < 85:
                new_series = Series(name=title, comic_child=[comic_child])
                db_session.add(new_series)
            else:
                series = db_session.query(Series).filter_by(name=maximum[0]).first()
                comic_child.seriesID = series.id

        db_session.commit()


def download_image(url, comic_id):
    if not url or "no-image" in url:
        return None
    r = rq.get(url, stream=True)
    if r.status_code != 200:
        sleep(30)
        r = rq.get(url, stream=True)
    path = "".join(['static/covers/', str(comic_id), '.png'])

    with open(path, 'ab+') as out_file:
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

def set_to_monday(d):
    while d.weekday() != 0:
        d = d - relativedelta(days=1)
    return d

def get_list_of_dates(base_url, start_date, end_date):
    week_diff = (end_date - start_date).days//7
    return [start_date + relativedelta(weeks=week) for week in xrange(week_diff)]

def find_wednesday(d):
    while d.weekday() != 3:
        d = d - relativedelta(days=1)
    return d


def get_marvel_data_frame():
    marvel = []
    images_links = {}

    headers = ["title", "url", "release_date", "image_link"]
    comics = pd.DataFrame(columns=headers)

    base_url = "http://marvel.com/comics/calendar/week/"
    start_date = datetime.date(datetime.now())

    start_date = set_to_monday(start_date)
    end_date = start_date + relativedelta(months=3)
    end_date = set_to_monday(end_date)

    dates = get_list_of_dates(base_url, start_date, end_date)

    for date in dates:
        url = "{}{}".format(base_url, date.strftime('%Y-%m-%d'))
        soup = bs(rq.get(url).text, 'html.parser')
        links = soup.findAll('a', {'class':'row-item-image-url'})
        nearest_wednesday = find_wednesday(date)

        for link in links:
            new_row = []
            image_tag = link.find('img')

            new_row.append(image_tag['title'])
            new_row.append(url)
            new_row.append(nearest_wednesday)
            new_row.append(image_tag['src'].replace('portrait_incredible', 'detail'))

            s = select([Comics.title]).where(Comics.title == image_tag['title'])
            result = db_session.execute(s).fetchone()

            if not result:
                comics.loc[len(comics)] = new_row

    return comics

def update_marvel_database():
    without_dups = get_marvel_data_frame()
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
