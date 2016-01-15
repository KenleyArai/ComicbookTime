
# coding: utf-8

# In[131]:
import re
import boto3
import shutil
import os.path
import requests as rq
from sqlalchemy.sql import select
from datetime import datetime
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup as bs
from fuzzywuzzy import process
from operator import itemgetter
from time import sleep
from app.models import Comic, Series
from PIL import Image
from StringIO import StringIO
TABLE = "comic"

def get_list_of_dates(base_url, start_date, end_date):
    week_diff = (end_date - start_date).days//7
    return [start_date + relativedelta(weeks=week) for week in xrange(week_diff)]

def find_wednesday(d):
    while d.weekday() != 2:
        d = d + relativedelta(days=1)
    return d

def find_sunday(d):
    while d.weekday() != 6:
        d = d - relativedelta(days=1)
    return d

def get_marvel_list(db):
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
            s = select([Comic.title]).where(Comic.title == image_tag['title'])
            result = db.session.execute(s).fetchone()

            if not result:
                img_link = image_tag['src'].replace('portrait_incredible', 'detail')
                new_comic = Comic(title=image_tag['title'].encode("utf8"),
                                     source_url=url,
                                     release_date=nearest_wednesday,
                                     image_link=img_link)
                comics.append(new_comic)
    return comics

def update_marvel_database(db):
    new_comics = get_marvel_list(db)
    update_db(new_comics,db)

def update_db(comics,db):
    for comic in comics:
        if "Guide" in comic.title:
            continue
        query = db.session.query(Comic).filter_by(title=comic.title).all()
        if not query:
            db.session.add(comic)
            find_series(comic,db)
            download_image(comic)
    db.session.commit()

def download_image(comic):
    filename = "{}.{}".format(comic.id, "jpg")
    conn = boto3.resource('s3')
    
    url = comic.image_link
    r = rq.get(url)

    with Image.open(StringIO(r.content)) as img:
        img.save(filename, 'JPEG') 
        conn.Object('comicbooktime', filename).put(Body=open(filename, 'rb'))

def find_series(c,db):
    series_title = c.title[:-4]
    print(series_title)
    like = "{percent}{title}{percent}".format(percent="%",title=series_title)
    result = Series.query.filter(Series.title.like(like)).all()
    print(result)

    if not result:
        new_series = Series(title=series_title, comics=[comic])
        db.session.add(new_series)
    else:
        options = process.extract(series_title, result)
        maximum = max(options, key=itemgetter(1))

        if maximum[1] < 85:
            new_series = Series(title=series_title, comics=[comic])
            db.session.add(new_series)
        else:
            comic.seriesID = result.id
    db.session.commit()
