from flask import Blueprint,render_template,session
from app.models import User
from flask_security.core import current_user
my_collection = Blueprint('my_collection', __name__)

@my_collection.route('/my_collection')
def my_collection_page():

    follows = [x.comics.all() for x in current_user.follows_series]
    bought = [list(set(current_user.bought_comics) & set(x)) for x in follows]
    bought = [x for x in bought if x]
    return render_template('my_collection.html', subs=bought, login=current_user.connections.full_name)
