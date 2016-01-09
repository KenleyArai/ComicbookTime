from app import db
from flask.ext.security import UserMixin, RoleMixin

from datetime import datetime

# Defining the table for the many-many relationship of User and Comic
bought_comics = db.Table('bought',
                         db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                         db.Column('comic_id', db.Integer, db.ForeignKey('comic.id')),
                         )

follows_series = db.Table('follows',
                         db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                         db.Column('series_id', db.Integer, db.ForeignKey('series.id')),
                          )
# Define models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String, unique=True)

    # many to many: A user can have many comics
    bought_comics = db.relationship('Comic',
                                    secondary=bought_comics,
                                    backref=db.backref('users', lazy='dynamic'))

    follows_series = db.relationship('Series',
                                     secondary=follows_series,
                                     backref=db.backref('users', lazy='dynamic'))

    roles = db.relationship('Role',
                            secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    connections = db.relationship('Connection',
                                  backref=db.backref('user', lazy='joined'), cascade="all", uselist=False)
    active = False
    def is_active(self):
        return True

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def __init__(self,google_id,active,roles):
        self.google_id = google_id
        self.active = active
        self.roles = roles

    def __repr__(self):
        return "<Google ID {}>".format(self.google_id)

class Connection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    provider_id = db.Column(db.String(255))
    full_name = db.Column(db.String(255))
    provider_user_id = db.Column(db.String(255))
    access_token = db.Column(db.String(255))
    secret = db.Column(db.String(255))
    display_name = db.Column(db.String(255))
    profile_url = db.Column(db.String(512))
    image_url = db.Column(db.String(512))
    rank = db.Column(db.Integer)
    

class Series(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True)
    comics = db.relationship('Comic', backref='Series',lazy='dynamic')

    def __init__(self,title,comics):
        self.title = title
        self.comics = comics

    def __repr__(self):
        return "<Title {}>".format(self.title)

class Comic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True)
    source_url = db.Column(db.String)
    image_link = db.Column(db.String, unique=True)
    release_date = db.Column(db.DateTime)
    series_id = db.Column(db.Integer, db.ForeignKey('series.id'))

    def __init__(self, title, source_url, image_link, release_date):
        self.title = title
        self.source_url = source_url
        self.image_link = image_link
        self.release_date = release_date

    def get_dict(self):
        return {'id':self.id,
                'title':self.title,
                'source_url':self.source_url,
                'image_link':self.image_link,
                'avail':self.release_date < datetime.now(),
                'release_date':datetime.date(self.release_date),
                'series_id':self.series_id}

    def __repr__(self):
        data = self.get_dict()
        return "<Title:{title}><Source Url:{source_url}><Image Link:{image_link}><Release Date:{release_date}>".format(**data)
