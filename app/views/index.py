from flask import Blueprint,render_template,session
from flask.ext.mobility.decorators import mobilized
from app.models import bought_comics,Comic,User
from flask_security.core import current_user
from app import db

index = Blueprint('index', __name__)

@index.route('/')
@index.route('/<int:page>')
@index.route('/index')
@index.route('/index/<int:page>')
def index_page(page=1):
    if current_user.is_authenticated: 
        series = current_user.follows_series
        bought = current_user.bought_comics

        comics = Comic.query.filter(Comic.series_id.in_(p.id for p in series) & Comic.id.notin_(p.id for p in bought)).order_by(Comic.release_date.asc())
        comics = comics.paginate(page, 9, False)

        # Getting a list of bought comics
        return render_template('index.html', login=current_user.connections.full_name, comics=comics)
        # Return the main page if there are no subscriptions
    return render_template('index.html') 

@mobilized(index_page)
def index_page(page=1):
    return "Hello World!"
