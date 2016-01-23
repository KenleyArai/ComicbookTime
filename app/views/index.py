from flask import current_app, render_template, jsonify
from rq.job import Job
from flask.ext.mobility.decorators import mobile_template
from flask_security.core import current_user
import json

from ..models import Comic, User
from .. import app, q, conn
@app.route('/')
@mobile_template('{mobile/}index.html')
def index(template):
    if current_user.is_authenticated:
        job = q.enqueue_call(func=get_comics, args=(current_user.id,), result_ttl=5000)
        return render_template(template,
                         login=current_user.connections.full_name,
                         job_id=job.get_id())
    return render_template(template)


def get_comics(uid):
    user = User.query.filter_by(id=uid).one()
    series = user.follows_series
    bought = user.bought_comics

    comics = Comic.query.filter(Comic.series_id.in_(p.id for p in series) & Comic.id.notin_(p.id for p in bought)).order_by(Comic.release_date.asc())
    comics = [x.get_dict() for x in comics.all()]
    return comics


@app.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):
    job = Job.fetch(job_key, connection=conn)
    if job.is_finished:
        return json.dumps(job.result), 200
    else:
        return 202
