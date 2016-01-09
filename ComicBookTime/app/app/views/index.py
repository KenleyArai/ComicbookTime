from flask import Blueprint,render_template,session
from app.models import bought_comics,Comic,User
from flask_security.core import current_user
from app import db

index = Blueprint('index', __name__)

def get_tuple_rows(l, columns):
    return [l[n:n+columns] for n in range(0, len(l), columns)]

@index.route('/')
@index.route('/index')
def index_page():
    if current_user.is_authenticated: 
        follows = [x.comics.all() for x in current_user.follows_series]
        follows = [x for sublist in follows for x in sublist]
        bought = current_user.bought_comics
        comics =[x.get_dict() for x in set(follows) - set(bought)]
        comics = get_tuple_rows(comics, 3)
        # Getting a list of bought comics
        return render_template('index.html', login=current_user.connections.full_name, comics=comics)
        # Return the main page if there are no subscriptions
    return render_template('index.html') 
