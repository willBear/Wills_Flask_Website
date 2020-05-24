from app import db

# The User class created inherits from db.Model, a base class for all
# models from Flask-SQLAlchemy. Fields are created as instances of the
# db.Column class, which takes the field type as an argument, plus other
# optional arguments that, allow us to indicate which fields are unique
# and indexed
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    # This method tells python how to print objects of this class, which
    # is going to be useful for debugging.
    def __repr__(self):
        return '<User {}>'.format(self.username)