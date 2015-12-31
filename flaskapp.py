import comic_tracking
import flask_resize

from flask import Flask, abort, request,redirect, url_for, render_template
from models import User, Comics, has_sub, Series, owns_comic
from fuzzyfinder import fuzzyfinder
from sqlalchemy.sql import select, insert, update

from database import db_session

app = Flask(__name__)

app.debug = True

marvel_urls = ["http://www.comiclist.com/index.php/newreleases/last-week",
               "http://www.comiclist.com/index.php/newreleases/this-week",
               "http://www.comiclist.com/index.php/newreleases/next-week"]

@app.route('/')
def index():
    subscriptions = db_session.query(has_sub).filter_by(user_id=1).all()
    user = db_session.query(User).filter_by(id=1).one()
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
        return render_template('main.html', comics=result)

    return render_template('main.html')


@app.route('/bought', methods=['GET', 'POST'])
def bought():
    u_id = request.args.get('u_id')
    c_id = request.args.get('c_id')
    comic = db_session.query(Comics).filter_by(id=c_id).one()
    user = db_session.query(User).filter_by(id=1).one()
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
        series = db_session.query(Series).filter_by(id=s_id).one()
        user = db_session.query(User).filter_by(id=1).one()
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
