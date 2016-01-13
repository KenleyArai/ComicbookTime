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

REDIRECT_URI = '/oauth2callback'

auth = Blueprint('auth', __name__)

@auth.route('/logout')
def logout():
    session.clear()
    logout_user()
    return render_template('index.html')



@login_failed.connect_via(app)
def on_login_failed(sender, provider, oauth_response):
    connection_values = get_connection_values_from_oauth_response(provider, oauth_response)
    connection_values['display_name'] = connection_values['display_name']['givenName'] +" "+ connection_values['display_name']['familyName']
    connection_values['full_name'] = connection_values['display_name']
    session['google_id'] = connection_values['provider_user_id']
    user = user_datastore.create_user(google_id=session['google_id'])
    user_datastore.commit()
    connection_values['user_id'] = user.id
    connect_handler(connection_values, provider)
    login_user(user)
    db.session.commit()
    return render_template('index.html')
