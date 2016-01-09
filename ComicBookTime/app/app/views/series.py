from flask import Blueprint,render_template,request,session,redirect,url_for
from flask_security.core import current_user
from app.models import Series, User, Comic

from flask.ext.security import login_required
from app import user_datastore,db
series = Blueprint('series', __name__)

def get_tuple_rows(l, columns):
    return [l[n:n+columns] for n in range(0, len(l), columns)]

@series.route('/series/<int:series_id>')
def series_page(series_id):
    series_comics = Comic.query.filter_by(series_id=series_id).all()
    
    print(series_comics)
    series_comics = get_tuple_rows(series_comics, 3)
    return render_template('series.html', login=current_user.connections.full_name, found=series_comics, series_id=series_id)


@series.route('/series/sub/<int:series_id>')
@login_required
def series_page_sub(series_id):
    series_comics = Series.query.filter_by(id=series_id).one()
    if series_comics not in current_user.follows_series:
        current_user.follows_series.append(series_comics)
        db.session.commit()

    return redirect(url_for('series.series_page', series_id=series_id))
