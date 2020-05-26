from datetime import datetime
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5

# Flask Login requires four items, and it can work with user models that
# are based on any database system
# is_authenticated: a property that is True if the user has valid credentials
# is_active: a property that is True if the user's account is active
# is_anonymous: False for regular users and True for a special anonymous user
# get_id(): A method that returns a unique identifier for the user as a string
from flask_login import UserMixin


# The User class created inherits from db.Model, a base class for all
# models from Flask-SQLAlchemy. Fields are created as instances of the
# db.Column class, which takes the field type as an argument, plus other
# optional arguments that, allow us to indicate which fields are unique
# and indexed
# Flask Login provides a mixin class called UserMixin that includes generic
# implementations that are appropriate for most user model classes.
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    # This method tells python how to print objects of this class, which
    # is going to be useful for debugging.
    def __repr__(self):
        return '<User {}>'.format(self.username)

    # With these two methods of generate and check password hashes, the
    # user is now able to do secure password generation and store passwords
    # Example: u = User(username = 'Susan', email = 'susan@example.com')
    #          u.check_password('mypassword')
    #          u.set_password('mypassword')
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # The new avatar() method returns the URL of the user's avatar image,
    # scaled to the requestsed size in pixels. For users that don't have an
    # avatar registered, an "identicon" image will be generated.
    def avatar(self, size):
        # To generate the MD5 hash, we first have to convert the emails to
        # lower case. then encode the string into bytes before passing it on
        # to the hash function.
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    # Declare many to many relationships in the users table
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'

    )


# Flask-Login knows nothing about databases, it needs the application's help
# in loading a user. The user loader is registered with Flask-login with the
# @login... decorator.
@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


# We are not declaring this table as a model, like we did for users and posts.
# Since this is an auxiliary table that has no data other than foreign keys,
# we do not need model class
followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))
