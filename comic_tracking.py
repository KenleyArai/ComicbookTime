
# coding: utf-8

# In[131]:

import re
import shutil
import os.path

import requests as rq
import pandas as pd

from sqlalchemy import Column, Boolean
from sqlalchemy.sql import select, exists
from datetime import datetime
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup as bs
from fuzzywuzzy import process
from models import Comics, Series
from database import engine, db_session
from operator import itemgetter
from time import sleep

TABLE = "comics"


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


def get_list_of_dates(base_url, start_date, end_date):
    week_diff = (end_date - start_date).days//7
    return [start_date + relativedelta(weeks=week) for week in xrange(week_diff)]

def find_wednesday(d):
    while d.weekday() != 3:
        d = d + relativedelta(days=1)
    return d

def find_sunday(d):
    while d.weekday() != 6:
        d = d - relativedelta(days=1)
    return d

def get_marvel_data_frame():
    comics = []

    base_url = "http://marvel.com/comics/calendar/week/"
    current_date = datetime.date(datetime.now())
    start_date = current_date - relativedelta(months=4)
    start_date = find_sunday(start_date)

    end_date = current_date + relativedelta(months=4)
    end_date = find_sunday(end_date)

    dates = get_list_of_dates(base_url, start_date, end_date)

    for date in dates:
        url = "{}{}".format(base_url, date.strftime('%Y-%m-%d'))
        soup = bs(rq.get(url).text, 'html.parser')
        links = soup.findAll('a', {'class':'row-item-image-url'})
        nearest_wednesday = find_wednesday(date)

        for link in links:
            image_tag = link.find('img')
            s = select([Comics.title]).where(Comics.title == image_tag['title'])
            result = db_session.execute(s).fetchone()

            if not result:
                img_link = image_tag['src'].replace('portrait_incredible', 'detail')
                new_comic = Comics(title=image_tag['title'].encode("utf8"),
                                   url=url.encode("utf8"),
                                   release_date=nearest_wednesday,
                                   image_link=img_link.encode("utf8"))
                comics.append(new_comic)
    return comics

def update_marvel_database():
    new_comics = get_marvel_data_frame()
    update_db(new_comics)

def update_db(comics):
    for comic in comics:
        if "Guide" in comic.title:
            continue
        query = db_session.query(Comics).filter_by(title=comic.title).all()
        if not query:
            db_session.add(comic)
            find_series(comic)
            download_image(comic)
    db_session.commit()

def download_image(comic):
    url = comic.image_link

    r = rq.get(url, stream=True)
    if r.status_code != 200:
        sleep(30)
        r = rq.get(url, stream=True)

    path = "{}{}{}".format("static/covers/",str(comic.id).encode("utf8"),".png")

    with open(path, 'ab+') as out_file:
        shutil.copyfileobj(r.raw, out_file)

def find_series(comic):
    series_title = comic.title[:-3]

    like = "{percent}{title}{percent}".format(percent="%",title=series_title.encode("utf8"))
    mask = Series.name.like(like)
    s = select([Series.name]).where(mask)

    result = [x[0] for x in db_session.execute(s).fetchall()]

    if not result:
        new_series = Series(name=series_title, comic_child=[comic])
        db_session.add(new_series)
    else:
        options = process.extract(series_title, result)
        maximum = max(options, key=itemgetter(1))

        if maximum[1] < 85:
            new_series = Series(name=series_title, comic_child=[comic])
            db_session.add(new_series)
        else:
            series = db_session.query(Series).filter_by(name=maximum[0]).first()
            comic.seriesID = series.id

    db_session.commit()
