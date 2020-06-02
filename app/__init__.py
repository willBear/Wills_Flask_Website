from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask_mail import Mail
from flask_bootstrap import Bootstrap


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

# Flask uses Python's logging package to write its logs, and this package already has the
# ability to send logs by email. All we need to do to get emails sent out on errors is to add
# a SMTPHandler instance to the Flask logger object, which is app.logger
if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Wills Website Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    if not os.path.exists('logs'):
        os.mkdir('logs')
    # The RotatingFileHandler class rotates the logs, ensuring that the log files do not grow
    # too large when the application runs for a long time. We are limiting the file to be 10KB
    # Keep the last 10 files as backup
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                       backupCount=10)
    # The logging formatting class provides custom formatting for the log messages. Since these
    # messages are going to a file, we include time stamp, the logging level, the message and the
    # source file and line number form where the log entry originated
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    # We also lower the logging level to the INFO category, both in the application logger and file
    # logger handler. The logging categories are DEBUG, INFO, WARNING, ERROR and CRITICAL
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Wills Website')

mail = Mail(app)

# We initialize bootstrap
bootstrap = Bootstrap(app)

# This is imported at the bottom is a workaround to circular imports.
# Putting it on the bottom avoids results from mutual references
from app import routes, models, errors
