import comic_tracking
import json
import time

from threading import Thread
from flask_oauth import OAuth
from views import main,find_view,series_view,my_collection
from flask import Flask, request,redirect, url_for, render_template, session
from models import User, Comics
from database import db_session
from global_var import GOOGLE_CLIENT_ID,GOOGLE_CLIENT_SECRET,REDIRECT_URI,SECRET_KEY

from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

import requests as rq

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

app = Flask(__name__)
app.debug = True
app.secret_key = SECRET_KEY
oauth = OAuth()
socketio = SocketIO(app, async_mode=async_mode)
thread = None

google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
                                                'response_type': 'code'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key=GOOGLE_CLIENT_ID,
                          consumer_secret=GOOGLE_CLIENT_SECRET)

marvel_urls = ["http://www.comiclist.com/index.php/newreleases/last-week",
               "http://www.comiclist.com/index.php/newreleases/this-week",
               "http://www.comiclist.com/index.php/newreleases/next-week"]

# Helper functions
def get_login():
    access_token = session.get('access_token')
    if access_token is None:
        return False
    access_token = access_token[0]

    headers = {'Authorization': 'OAuth '+access_token}
    req = rq.get('https://www.googleapis.com/oauth2/v1/userinfo',headers=headers)

    if req.status_code == 401:
        return False
    login = json.loads(req.text)
    return login

def check_login(login, else_page_func, *args):
    if not login:
        session.pop('access_token', None)
        return render_template('main.html')
    else:
        return else_page_func(login, *args)

def with_out_check_login(login, else_page_func, *args):
    return else_page_func(login, *args)


# Pages without views

@app.route('/logout')
def logout():
    session.pop('access_token', None)
    return render_template('main.html')

@app.route('/login')
def login():
    callback=url_for('authorized', _external=True)
    return google.authorize(callback=callback)

@app.route('/bought', methods=['GET', 'POST'])
def bought():

    login = get_login()
    if not login:
        session.pop('access_token', None)
        return render_template('main.html')

    c_id = request.args.get('c_id')
    comic = db_session.query(Comics).filter_by(id=c_id).one()       # Getting specific comic
    user = db_session.query(User).filter_by(id=login['id']).one()   # Getting specific user
    user.comic_child.append(comic)                                  # Updating the bought relation
    db_session.commit()

    return redirect(url_for('index'))

@app.route(REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    return redirect(url_for('index'))

@google.tokengetter
def get_access_token():
    return session.get('access_token')

@app.route('/marvel_update')
def marvel_update():
    login = get_login()
    if login['given_name'] != "Kenley":
        return redirect(url_for('index'))
    comic_tracking.update_marvel_database(marvel_urls)
    return redirect(url_for('index'))

# Pages with views
@app.route('/')
def index():
    init_thread()
    login = get_login()
    return check_login(login, main.main)

@app.route('/my_collection')
def my_c():
    login = get_login()
    return check_login(login, my_collection.my_collection)

@app.route('/find', methods=['GET', 'POST'])
def find():
    login = get_login()
    return with_out_check_login(login, find_view.find_view, request)

@app.route('/series', methods=['GET'])
def series():
    login = get_login()
    return check_login(login, series_view.series_view, request)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

# Sockets

def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        time.sleep(10)
        count += 1
        socketio.emit('my response',
                      {'data': 'Server generated event', 'count': count},
                      namespace='/test')

def init_thread():
    global thread
    if thread is None:
        thread = Thread(target=background_thread)
        thread.daemon = True
        thread.start()

@socketio.on('unbuy', namespace='/test')
def test_message(message):
    c_id = message['data']
    login = get_login()

    if not login:
        session.pop('access_token', None)

    comic = db_session.query(Comics).filter_by(id=c_id).one()       # Getting specific comic
    user = db_session.query(User).filter_by(id=login['id']).one()   # Getting specific user
    user.comic_child.remove(comic)                                  # Updating the bought relation
    db_session.commit()

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)

if __name__ == '__main__':
    socketio.run(app, debug=True)
