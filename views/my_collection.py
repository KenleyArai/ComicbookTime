from flask import redirect,render_template,url_for
from ..database import db_session

from ..helper_functions import *

def my_collection(login):
    user = get_user_by_uid(login['id']).one()
    subscriptions = get_subs_by_uid(login['id']).all()

    bought = user.comic_child

    subs = [x[1] for x in subscriptions]

    if subs: # if we subsciptions exist
        c = []
        titles = []
        for r in subs:
            new_row = []
            # Retrieving each series by their series ID in desc order
            new_comics = [x for x in db_session.query(Comics).filter_by(seriesID=r).order_by(Comics.id.desc()).all()]
            for nc in new_comics:
                if nc in bought:
                    new_row.append(nc.get()) # Need to find a better way than a get method
            if new_row:
                c.append(new_row)
        c = [get_tuple_rows(x, 5) for x in c]
        return render_template('my_collection.html', subs=c, login=login['given_name'])
    # Return the main page if there are no subscriptions
    return render_template('main.html')
