from flask import render_template
from models import Comics
from database import db_session


def find_view(login, request):
    if request.method == 'POST':
        search = request.form['comic']
        like_condition = "".join(["%", search,"%"])

        query = db_session.query(Comics).filter(Comics.title.like(like_condition))
        query = query.all()
        comics = [x.get() for x in query]
        comics = [comics[n:n+3] for n in range(0, len(comics), 3)]
        return render_template('find.html',
                               found=comics,
                               login=login['given_name'] if login else None)
    return render_template('find.html')
