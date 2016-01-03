from database import db_session
from models import User, Comics, Series

def convet_comic_to_tuples(l):
    return [x.get() for x in l]

def get_series_by_series_id(s_id):
    return db_session.query(Series).filter_by(id=s_id)

def get_comics_by_series_id(s_id):
    return db_session.query(Comics).filter_by(seriesID=s_id)

def get_all_comics_by_series_id(s_id, convert=False):
    if convert:
        return convet_comic_to_tuples(get_comics_by_series_id(s_id).all())
    return get_comics_by_series_id(s_id).all()

def get_user_by_uid(uid):
    return db_session.query(User).filter_by(id=uid)

def get_tuple_rows(l, columns):
    return [l[n:n+columns] for n in range(0, len(l), columns)]
