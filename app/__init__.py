from flask import Flask
from config import Config

app = Flask(__name__)

# Tell Flask to read and apply the config file, done right after
# the Flask application instance is created
# The configuration items can be accessed with a dictionary syntax from
# app.config.
app.config.from_object(Config)

# This is imported at the bottom is a workaround to circular imports.
# Putting it on the bottom avoids results from mutual references

from app import routes
