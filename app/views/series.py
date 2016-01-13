from flask import Blueprint,render_template,request,session,redirect,url_for
from flask_security.core import current_user
from app.models import Series, User, Comic

from flask.ext.security import login_required
from app import user_datastore,db
series = Blueprint('series', __name__)


@series.route('/series/<int:series_id>')
def series_page(series_id):
    comics = Comic.query.filter_by(series_id=series_id)
    comics = comics.paginate(1, 9, False)

    return render_template('series.html', login=current_user.connections.full_name, found=comics, series_id=series_id)


@series.route('/series/sub/<int:series_id>')
@login_required
def series_page_sub(series_id):
    series_comics = Series.query.filter_by(id=series_id).one()
    if series_comics not in current_user.follows_series:
        current_user.follows_series.append(series_comics)
        db.session.commit()

    return redirect(url_for('series.series_page', series_id=series_id))