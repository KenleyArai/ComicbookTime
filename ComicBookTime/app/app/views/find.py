from flask import Blueprint,render_template,request,session
from flask_security.core import current_user
from app.models import Comic
from app import db

find = Blueprint('find', __name__)

def get_tuple_rows(l, columns):
    return [l[n:n+columns] for n in range(0, len(l), columns)]

@find.route('/find', methods=['GET','POST'])
def find_page():
    comics=[]
    if request.method == 'POST':
        search = request.form['comic']

        bought = []
        new_list = []

        like_condition = "".join(["%",search,"%"])
        query = db.session.query(Comic).filter(Comic.title.like(like_condition)).all()

        new_list = [x.get_dict() for x in query]
        comics = get_tuple_rows(new_list, 3)

    if not current_user.is_authenticated:
        return render_template('find.html',found=comics)
    else:
        return render_template('find.html',found=comics,login=current_user.connections.full_name)
