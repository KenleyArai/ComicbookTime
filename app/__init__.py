from flask import Flask,render_template,session,request
from flask_sqlalchemy import SQLAlchemy
from flask.ext.social import Social, login_failed
from flask.ext.social.views import connect_handler
from flask.ext.social.utils import get_connection_values_from_oauth_response
from flask.ext.social.datastore import SQLAlchemyConnectionDatastore
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required,login_user
from flask_security.core import current_user
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask.ext.heroku import Heroku

import os

app = Flask(__name__)


app.config['DEBUG'] = os.environ["DEBUG"]
app.config['SQLALCHEMY_ECHO'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]


app.config['SOCIAL_GOOGLE'] = {
                'consumer_key':os.environ['GOOGLE_ID'],
                'consumer_secret':os.environ['GOOGLE_SECRET']
                }

app.secret_key = os.environ['SECRET']

app.config['SECURITY_LOGIN_URL'] = "/none"

heroku = Heroku()

db = SQLAlchemy(app)
from app.models import User, Role, Connection, Comic

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)
social = Social(app, SQLAlchemyConnectionDatastore(db, Connection))
heroku.init_app(app)
from views.index import index
from views.find import find
from views.my_collection import my_collection
from views.series import series
from views.login import auth
from views.marvel_update import marvel_update
from views.bought import bought

app.register_blueprint(index)
app.register_blueprint(find)
app.register_blueprint(my_collection)
app.register_blueprint(series)
app.register_blueprint(auth)
app.register_blueprint(marvel_update)
app.register_blueprint(bought)


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
@app.before_first_request
def do_this():
    if not Role.query.first():
        db.create_all()
        user_datastore.create_role(name="admin",description="")
        user_datastore.create_role(name="user",description="")
        db.session.commit()

@socketio.on('buy')
def buy(message):
    c_id = message['data']

    comic = Comic.query.filter_by(id=c_id).one()
    current_user.bought_comics.append(comic)                                  # Updating the bought relation
    db.session.commit()
    emit('my response')

@socketio.on('unbuy')
def unbuy(message):
    c_id = message['data']
    comic = db.session.query(Comic).filter_by(id=c_id).one()                  # Getting specific comic
    current_user.bought_comics.remove(comic)                                  # Updating the bought relation
    db.session.commit()
    emit('my response')

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected', request.sid)
    emit('my response')
