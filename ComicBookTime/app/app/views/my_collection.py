from flask import Blueprint,render_template,session
from app.models import User
from flask_security.core import current_user
my_collection = Blueprint('my_collection', __name__)

@my_collection.route('/my_collection')
def my_collection_page():

    follows = [x.comics.all() for x in current_user.follows_series]
    bought = [list(set(current_user.bought_comics) & set(x)) for x in follows]
    comics = []
    for x in bought:
        comic_row = []
        for i in x:
            comic_row.append(i.get_dict())
        if comic_row:
            comics.append(comic_row)
    return render_template('my_collection.html', subs=comics, login=current_user.connections.full_name)
