import comic_tracking
import json
from flask_oauth import OAuth

from datetime import datetime

from flask import Flask, request,redirect, url_for, render_template, session
from models import User, Comics, has_sub, Series
from sqlalchemy.sql import select

from database import db_session
import requests as rq

GOOGLE_CLIENT_ID = ''
GOOGLE_CLIENT_SECRET = ''
REDIRECT_URI = '/oauth2callback'


app = Flask(__name__)

app.debug = True
SECRET_KEY = 'development key'
app.secret_key = SECRET_KEY
oauth = OAuth()

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

def check_login():
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))
    access_token = access_token[0]

    headers = {'Authorization': 'OAuth '+access_token}
    req = rq.get('https://www.googleapis.com/oauth2/v1/userinfo',headers=headers)

    if req.status_code == 401:
        return False
    login = json.loads(req.text)
    if login['given_name'] != "Kenley":
        return False
    return login


@app.route('/')
def index():

    login = check_login()

    if not login:
        session.pop('access_token', None)
        return redirect(url_for('login'))

    user = db_session.query(User).filter_by(id=login['id']).first()

    if not user:
        user = User(id=login['id'],name=login['given_name'])
        db_session.add(user)
        db_session.commit()

    subscriptions = db_session.query(has_sub).filter_by(user_id=login['id']).all()
    bought = user.comic_child
    result = [x[1] for x in subscriptions]

    if result:
        c = []
        for r in result:
            new_comics = [x for x in db_session.query(Comics).filter_by(seriesID=r).order_by(Comics.id.desc()).all()]
            for nc in new_comics:
                if nc not in bought:
                    c.append(nc.get())

        result = [c[n:n+3] for n in range(0, len(c), 3)]
        return render_template('main.html', comics=result, login=login['given_name'])

    return render_template('main.html')

@app.route('/login')
def login():
    callback=url_for('authorized', _external=True)
    return google.authorize(callback=callback)

@app.route(REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    return redirect(url_for('index'))


@google.tokengetter
def get_access_token():
    return session.get('access_token')

@app.route('/bought', methods=['GET', 'POST'])
def bought():

    login = check_login()

    u_id = request.args.get('u_id')
    c_id = request.args.get('c_id')
    comic = db_session.query(Comics).filter_by(id=c_id).one()
    user = db_session.query(User).filter_by(id=login['id']).one()
    user.comic_child.append(comic)
    db_session.commit()

    return redirect(url_for('index'))

@app.route('/find', methods=['GET', 'POST'])
def find():
    if request.method == 'POST':
        search = request.form['comic']
        cmd = None
        if ">" in search:
            search = search.split(">")
            cmd = search[0]
            search = search[1]

        columns = [Comics.id,
                   Comics.title,
                   Comics.release_date,
                   Comics.image_link,
                   Comics.notes,
                   Comics.availability,
                   Comics.seriesID]

        mask = "".join(["%", search,"%"])
        mask = Comics.title.like(mask)
        s = select(columns).where(mask)

        result = [x for x in db_session.execute(s).fetchall()]

        if cmd:
            if "A" in cmd or "a" in cmd:
                result = [x for x in result if x[5]]
            elif 'U' in cmd or 'u' in cmd:
                result = [x for x in result if not x[5]]
        result = [result[n:n+3] for n in range(0, len(result), 3)]

        return render_template('find.html', found=result)
    return render_template('find.html', found={})


@app.route('/series', methods=['GET'])
def series():
    s_id = request.args.get('id')
    sub = request.args.get('sub')
    if not sub:
        series_comics = db_session.query(Comics).filter_by(seriesID=s_id).all()
        series_comics = [x.get() for x in series_comics]
        result = [series_comics[n:n+3] for n in range(0, len(series_comics), 3)]

        return render_template('series.html', found=result, series_id=s_id)
    else:
        login = check_login()
        series = db_session.query(Series).filter_by(id=s_id).one()
        user = db_session.query(User).filter_by(id=login['id']).one()
        user.series_child.append(series)
        db_session.commit()
    return redirect(url_for('index'))

@app.route('/marvel_update')
def marvel_update():
    comic_tracking.update_marvel_database(marvel_urls)
    return redirect(url_for('index'))

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.run()
