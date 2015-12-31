import comic_tracking
import flask_resize

from flask import Flask, abort, request,redirect, url_for, render_template
from models import User, Comics
from fuzzyfinder import fuzzyfinder
from sqlalchemy.sql import select

from database import db_session

app = Flask(__name__)

app.debug = True

marvel_urls = ["http://www.comiclist.com/index.php/newreleases/last-week",
               "http://www.comiclist.com/index.php/newreleases/this-week",
               "http://www.comiclist.com/index.php/newreleases/next-week"]

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/find', methods=['GET', 'POST'])
def find():
    if request.method == 'POST':
        columns = [Comics.id,
                   Comics.title,
                   Comics.release_date,
                   Comics.image_link,
                   Comics.notes,
                   Comics.availability]

        mask = "".join(["%", request.form['comic'], "%"])
        mask = Comics.title.like(mask)
        s = select(columns).where(mask)

        result = [x for x in db_session.execute(s).fetchall()]
        result = [result[n:n+3] for n in range(0, len(result), 3)]

        return render_template('find.html', found=result)
    return render_template('find.html', found={})

@app.route('/marvel_update')
def marvel_update():
    comic_tracking.update_marvel_database(marvel_urls)
    return redirect(url_for('index'))

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.run()
