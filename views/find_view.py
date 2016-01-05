import os,sys
parentdir = os.path.dirname(__file__)
sys.path.insert(0,parentdir)

from flask import render_template
from models import Comics
from database import db_session
from helper_functions import *
from sqlalchemy import desc

def find_view(login, request):
    if request.method == 'POST':
        search = request.form['comic']

        like_condition = "".join(["%", search,"%"])
        query = db_session.query(Comics).filter(Comics.title.like(like_condition)).order_by(desc(Comics.release_date))
        query = query.all()
        bought = []
        if login:
            user = get_user_by_uid(login['id']).one()
            bought = user.series_child
        new_list = []
        for q in query:
            if q not in bought:
                new_list.append(q.get()) # Need to find a better way than a get method
        comics = get_tuple_rows(new_list, 3)
        return render_template('find.html',
                               found=comics,
                               login=login['given_name'] if login else None)
    return render_template('find.html', login=None if not login else login['given_name'])

