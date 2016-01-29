from flask import Flask, render_template, session, request
from flask_sqlalchemy import SQLAlchemy
from flask.ext.social import Social, login_failed
from flask.ext.social.views import connect_handler
from flask.ext.social.utils import get_connection_values_from_oauth_response
from flask.ext.social.datastore import SQLAlchemyConnectionDatastore
from flask.ext.security import Security, SQLAlchemyUserDatastore, login_user
from flask_security.core import current_user
from flask_socketio import SocketIO, emit
from flask.ext.heroku import Heroku
from flask.ext.mobility import Mobility
from flask.ext.triangle import Triangle


import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from rq import Queue
import worker

conn = worker.conn

import os

app = Flask(__name__)
q = Queue(connection=conn)
Triangle(app)

app.config['DEBUG'] = os.environ["DEBUG"]
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]


app.config['SOCIAL_GOOGLE'] = {
                       'consumer_key': os.environ['GOOGLE_ID'],
                       'consumer_secret': os.environ['GOOGLE_SECRET']
                      }

app.secret_key = os.environ['SECRET']

app.config['SECURITY_LOGIN_URL'] = "/none"

heroku = Heroku()

Mobility(app)
db = SQLAlchemy(app)

from app.models import User, Role, Connection, Comic

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)
social = Social(app, SQLAlchemyConnectionDatastore(db, Connection))
heroku.init_app(app)

from views import index, search

@login_failed.connect_via(app)
def on_login_failed(sender, provider, oauth_response):
    connection_values = get_connection_values_from_oauth_response(provider, oauth_response)
    connection_values['display_name'] = connection_values['display_name']['givenName'] +" "+ connection_values['display_name']['familyName']
    connection_values['full_name'] = connection_values['display_name']
    session['google_id'] = connection_values['provider_user_id']
    user = user_datastore.create_user(google_id=session['google_id'])
    user_datastore.commit()
    connection_values['user_id'] = user.id
    connect_handler(connection_values, provider)
    login_user(user)
    db.session.commit()
    return render_template('index.html')

async_mode = None

if async_mode is None:
    try:
        import eventlet
        async_mode = 'eventlet'
    except ImportError:
        pass

    if async_mode is None:
        try:
            from gevent import monkey
            async_mode = 'gevent'
        except ImportError:
            pass

    if async_mode is None:
        async_mode = 'threading'

    print('async_mode is ' + async_mode)

if async_mode == 'eventlet':
    import eventlet
    eventlet.monkey_patch()
elif async_mode == 'gevent':
    from gevent import monkey
    monkey.patch_all()

socketio = SocketIO(app, async_mode=async_mode)

@socketio.on("get_comics")
def get_comics():
    user = User.query.filter_by(id=current_user.id).one()
    series = user.follows_series
    bought = user.bought_comics

    comics = Comic.query.filter(Comic.series_id.in_(p.id for p in series) & Comic.id.notin_(p.id for p in bought)).order_by(Comic.release_date.asc())
    comics = [x.get_dict() for x in comics.all()]

    emit('send_comics', comics)

@socketio.on("get_all_comics")
def get_all_comics():
    comics = [x.get_dict() for x in Comic.query.all()]
    emit('send_comics', comics)

@socketio.on('joined_message')
def joined_chat(data):
    emit('message', data)

@socketio.on('send_message')
def handle_message(data):
    emit('message', data)
