from flask import Blueprint,render_template,session,url_for,redirect
from flask.ext.social import Social, login_failed
from flask.ext.social.views import connect_handler
from flask.ext.social.utils import get_connection_values_from_oauth_response
from flask.ext.security.utils import logout_user, login_user
from flask_security.core import current_user
from flask_oauth import OAuth
import requests as rq
import app
from app import db,user_datastore,social
from app.models import User,Role

import json

auth = Blueprint('auth', __name__)

@auth.route('/logout')
def logout():
    session.clear()
    logout_user()
    return render_template('index.html')

