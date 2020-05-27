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

# We are not declaring this table as a model, like we did for users and posts.
# Since this is an auxiliary table that has no data other than foreign keys,
# we do not need model class
followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))


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
        # User is the right side entity of the relationship, left side entity
        # is the parent class. we use the same class on both sides since this is
        # a self referential relationship
        'User', secondary=followers,
        # Primaryjoin indicates the condition that links the left side entity with
        # the association table. The followers.c.follower_id expression reference the
        # follower_id column on the association table
        primaryjoin=(followers.c.follower_id == id),
        # Similar for primary join where we join followed id
        secondaryjoin=(followers.c.followed_id == id),
        # Backref defines how this relationship will be access from the right side entity.
        # From the left side, the relationship is named followed so from the right side
        # we are going to use the name followers to reperesent al the left side users
        # that are linked to the target user in the right side.
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
    )

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    # The is_following method isses a query on the followed relationship to
    # check if a link between two users already exists. It looks for items in
    # the association table that have the left side foreign key set to the self user,
    # and the right side set to the user argument.
    # The argument will either return a 0 or a 1
    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    #
    def followed_posts(self):
        # In the join operation on the posts table, the first argument is the
        # followers association table, and the second argument is the join
        # condition. This call creates a temp table that combines data from
        # posts and followers data tables. The data is going to be merged according
        # to the condition that we have passed as argument
        # The followed_id field must equal to the user_id of the posts table.
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)
        # This does not apply to your own posts, so we query the posts table
        # and find id's for ourselves, then we union the table and order the
        # timestamp by time descending
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())
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
