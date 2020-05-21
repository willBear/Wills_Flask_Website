from flask import Flask

app = Flask(__name__)

# This is imported at the bottom is a workaround to circular imports.
# Putting it on the bottom avoids results from mutual references

from app import routes
