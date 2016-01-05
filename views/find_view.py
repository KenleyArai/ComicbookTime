import sys

sys.path.append('../')
from flask import render_template
from models import Comics
from database import db_session
from helper_functions import *


def find_view(login, request):
    if request.method == 'POST':
        search = request.form['comic']

        like_condition = "".join(["%", search,"%"])
        query = db_session.query(Comics).filter(Comics.title.like(like_condition))
        query = query.all()
        user = get_user_by_uid(login['id']).one()

        bought = user.comic_child
        new_list = []

        for q in query:
            if q not in bought:
                new_list.append(q.get()) # Need to find a better way than a get method

        comics = get_tuple_rows(new_list, 3)
        return render_template('find.html',
                               found=comics,
                               login=login['given_name'] if login else None)
    return render_template('find.html', login=login['given_name'] if login else None)

