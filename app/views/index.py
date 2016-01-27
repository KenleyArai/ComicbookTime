from flask import render_template
from flask.ext.mobility.decorators import mobile_template
from flask_security.core import current_user
from .. import app

@app.route('/')
@mobile_template('{mobile/}index.html')
def index(template):
    if current_user.is_authenticated:
        return render_template(template, login=current_user.connections.full_name)
    return render_template(template)
