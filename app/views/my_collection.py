from flask import render_template
from flask.ext.mobility.decorators import mobile_template
from flask_security.core import current_user
from app import app

@app.route('/my_collection')
def my_collection():
    if current_user.is_authenticated:
        return render_template("my_collection.html", login=current_user.connections.full_name)
    return render_template(template)
