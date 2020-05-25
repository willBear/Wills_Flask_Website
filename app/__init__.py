from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config


app = Flask(__name__)
# Tell Flask to read and apply the config file, done right after
# the Flask application instance is created
# The configuration items can be accessed with a dictionary syntax from
# app.config.
app.config.from_object(Config)

# We first add a db object represents the database.
db = SQLAlchemy(app)

# We add another database that represents the migration engine
migrate = Migrate(app, db)

# Initializes the login, which manages the user logged-in state, so that
# users can log into application and then navigate to different pages while
# the applications "remembers" that the user is logged in.
# It even provides the "remember me" functionality that allows users to
# remain logged in even after closing the browser window
login = LoginManager(app)

# Flask-Login provides a very useful feature that forces users to log in
# before they can view certain pages of the application. If user who is
# not logged in tries to view a protected page, Flask-Login will automatically
# redirect the user to the login form, and only redirect back to the page the
# user wanted to view after the login process is complete.
# For this feature to be implemented, Flask_login needs to know what is the view
# function that handles logins. The 'login' value above is the function name for
# the login view. In other words, the name you would use in a url_for() call to
# get the URL
login.login_view = 'login'

# This is imported at the bottom is a workaround to circular imports.
# Putting it on the bottom avoids results from mutual references
from app import routes, models
