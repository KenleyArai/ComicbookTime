from flask import Blueprint,render_template,request,session
from flask_security.core import current_user
from app.models import Comic
from app import db

find = Blueprint('find', __name__)

@find.route('/find', methods=['GET','POST'])
@find.route('/find/<int:page>', methods=['GET','POST'])
def find_page(page=1):
    comics=[]

    search = ""

    if request.method == 'POST':
        search = request.form['comic']
    bought = []
    new_list = []

    like_condition = "".join(["%",search,"%"])
    query = Comic.query.filter(Comic.title.like(like_condition)).order_by(Comic.release_date.desc())
    pages = query.paginate(page,9, False)

    if not current_user.is_authenticated:
        return render_template('find.html',found=pages)
    else:
        return render_template('find.html',found=pages,login=current_user.connections.full_name)
