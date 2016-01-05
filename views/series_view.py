
import sys

sys.path.append('../')

from flask import redirect,render_template,url_for
from database import db_session
from helper_functions import get_all_comics_by_series_id, get_tuple_rows, convet_comic_to_tuples
from helper_functions import get_series_by_series_id, get_user_by_uid

def series_view(login, request):
    s_id = request.args.get('id')
    sub = request.args.get('sub')
    if not sub:
        series_comics = get_all_comics_by_series_id(s_id, convert=True)
        series_comics = get_tuple_rows(series_comics, 3)
        return render_template('series.html', login=login['given_name'],found=series_comics, series_id=s_id)
    else:
        series = get_series_by_series_id(s_id).one()
        user = get_user_by_uid(login['id']).one()
        user.series_child.append(series)
        db_session.commit()
    return redirect(url_for('index'))
