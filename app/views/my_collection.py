from flask import Blueprint,render_template,session
import sys
from itertools import groupby
from app.models import User
from flask_security.core import current_user
my_collection = Blueprint('my_collection', __name__)

@my_collection.route('/my_collection')
def my_collection_page():
    bought = current_user.bought_comics
    
    groups = []
    uniquekeys = []
    for k, g in groupby(bought, lambda x: x.series_id):
       groups.append(list(g))

    for l in groups:
        l.sort(key=lambda x: x.release_date, reverse=True)

    return render_template('my_collection.html', subs=groups, login=current_user.connections.full_name)
