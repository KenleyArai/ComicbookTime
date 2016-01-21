from flask import Blueprint,render_template,redirect,session,url_for
from app.models import Comic,User
from flask_security.core import current_user
from app import db

bought = Blueprint('bought', __name__)

@bought.route('/bought/<int:comic_id>')
def bought_page(comic_id):
    comic = Comic.query.filter_by(id=comic_id).one()
    if comic not in current_user.bought_comics:
        current_user.bought_comics.append(comic)
    db.session.commit()
    return redirect(url_for('index.index_page'))
