import comic_tracking

from flask import Flask, abort, redirect, url_for
from models import Users, Comics 

from database import db_session

app = Flask(__name__)
app.debug = True

marvel_urls = ["http://www.comiclist.com/index.php/newreleases/last-week",
               "http://www.comiclist.com/index.php/newreleases/this-week",
               "http://www.comiclist.com/index.php/newreleases/next-week"]

@app.route('/')
def index():
    return "Test"

@app.route('/marvel_update')
def marvel_update():
    comic_tracking.update_marvel_database(marvel_urls) 
    return redirect(url_for('index'))

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.run()
