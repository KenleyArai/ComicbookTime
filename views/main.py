import os,sys
parentdir = os.path.dirname(__file__)
sys.path.insert(0,parentdir)

from flask import render_template
from models import User,Comics,has_sub
from database import db_session

def main(login):
    """
    the index view, input is the login information.
    This function assumes that the user has already logged in.
    """
    user = db_session.query(User).filter_by(id=login['id']).first()

    # Checking if the user existed in the database if it doesn't add them to
    # the database this assumes that they already have logged in via google
    if not user:
        user = User(id=login['id'],name=login['given_name'])
        db_session.add(user)
        db_session.commit()

    subscriptions = db_session.query(has_sub).filter_by(user_id=login['id']).all()

    # Getting a list of bought comics
    bought = user.comic_child

    # x[1] because a tuple is return i.e (0, 3) where 0 is the row number and 3 is the series ID
    result = [x[1] for x in subscriptions]

    if result: # if we subsciptions exist
        c = []
        for r in result:
            # Retrieving each series by their series ID in desc order
            new_comics = [x for x in db_session.query(Comics).filter_by(seriesID=r).order_by(Comics.id.desc()).all()]
            for nc in new_comics:
                if nc not in bought:
                    c.append(nc.get()) # Need to find a better way than a get method

        c = sorted(c, key=lambda x: not x[5]) # Sorting by availability
        result = [c[n:n+3] for n in range(0, len(c), 3)] # Build helper function to do this
        return render_template('main.html', comics=result, login=login['given_name'])
    # Return the main page if there are no subscriptions
    return render_template('main.html')
