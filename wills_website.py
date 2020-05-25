#-------------------------------------------------------------------------------
# File Name: wills_website.py
#
# Purpose:
# This file defines the Flask application instance.
#-------------------------------------------------------------------------------

# The Flask application instance is called app and is a member of the app package.
# Statement below imports the app variable that is a member  of the app package

from app import app, db
from app.models import User, Post

@app.shell_context_processor
def make_shell_context():
    return {'db':'db','User':User,'Post':Post}