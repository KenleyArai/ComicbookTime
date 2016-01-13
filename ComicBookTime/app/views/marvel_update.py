from flask_security import roles_accepted
from app.scripts import comic_tracking
from app import db
from flask import Blueprint,render_template,session,url_for,redirect

marvel_update = Blueprint('marvel_update', __name__)

@marvel_update.route('/marvel_update')
def marvel_update_page():
    comic_tracking.update_marvel_database(db)
    return redirect(url_for('index.index_page'))
