import os
basedir = os.path.abspath(os.path.dirname(__file__))
# The configuration settings are defined as class variables inside the config
# class. As the application needs more configuration items, they can be added
# to this class, and later if theres need to have more than one configuration
# set, create subclasses to it.

# The SECRET_KEY configuration variable as the only configuration item is an
# important part in most Flask Applications. Flask and some of its extensions
# use the value of the secret key as a cryptographic key, useful to generate
# signatures or tokens.

# Flask WTF extension uses it to protect web forms against nasty attacks called
# Cross-Site Request Forgery.
class Config(object):
    # The value of the secret key is set as an expression with two terms, joined
    # by the or operator. The first term looks for the value of an environment
    # variable, and the second is just a hardcoded string.
    # The value sourced from an environment variable is preferred, but if the
    # environment does not defined the variable, then the hardcoded string is used

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # The Flask-SQLAlchemy extension takes the location of the application's
    # database from the SQLALCHEMY_DATABASE_URI configuration variable. We take
    # the database URL from the DATABASE_URL environment variable, and if that
    # isn't defined, we configure a database named app.db located in the main di-
    # rectory of the application, which is stored in the basedir variable
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///'\
        + os.path.join(basedir, 'app.db')

    # The SQLALCHEMY_TRACK_MODIFICATIONS configuration option is set to False to
    # disable a feature of Flask-SQLAlchemy that we do not need need, which is to
    # signal the application every time a change is about to be made in the database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
