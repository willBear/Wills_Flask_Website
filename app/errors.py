from flask import render_template
from app import app, db

"""
The error functions work very similarly to view functions. For these two errors,
we're returning the contents of their respective templates. For all the view functions
so far, we dod not need to add a second return value because it defaults to 200. 
"""
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404
"""
The error handler 500 could be invoked after a database error, which was actually the 
case with the username duplicate above. 
"""
@app.errorhandler(500)
def not_found_error(error):
    # To make any failed database sessions do not interfere with any database accesses
    # triggered by the template, issue a session rollback
    db.session.rollback()

    return render_template('500.html'), 500