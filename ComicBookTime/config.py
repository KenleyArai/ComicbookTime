import os
base_dir = os.path.abspath(os.path.dirname(__file__))

database = {'type':'sqlite',
            'base':base_dir,
            'db':'comics.db'}

DEBUG = True
SQLALCHEMY_ECHO = False
REDIRECT_URI = '/oauth2callback'
SECURITY_LOGIN_URL = "/none"
SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]
