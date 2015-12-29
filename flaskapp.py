import comic_tracking

from flask import Flask, abort, request,redirect, url_for, render_template
from models import Users, Comics 
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
    return "Test"

@app.route('/find', methods=['GET', 'POST'])
def find():
    if request.method == 'POST':
        s = select([Comics.title]).where(Comics.title.like("%" + request.form['comic'] + "%"))
        result = [x[0] for x in db_session.execute(s).fetchall()]
        return render_template('find.html', found=result)
    return render_template('find.html') 

@app.route('/marvel_update')
def marvel_update():
    comic_tracking.update_marvel_database(marvel_urls) 
    return redirect(url_for('index'))

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.run()
