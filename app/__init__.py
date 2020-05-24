from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

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

# This is imported at the bottom is a workaround to circular imports.
# Putting it on the bottom avoids results from mutual references
from app import routes, models
