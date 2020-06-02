# -------------------------------------------------------------------------------
# File Name: Routes.py
#
# Purpose:
# The routes are the different URLS that the application implements. Handlers of
# for the application routes are written as Python Functions, called view
# functions. View functions are mapped to one or more route URLs so that Flask
# knows what logic to execute when a client requests a given URL
# -------------------------------------------------------------------------------

# The operation that converts a template into a complete HTML page is called
# rendering. This render_template function takes a template filename and a
# variable list of template arguments and returns the same template, with actual
# values
# The render_template() function invokes the Ninja 2 template engine that comes
# bundled with the Flask Framework

from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm
from app.models import User, Post
from werkzeug.urls import url_parse
from app.forms import ResetPasswordRequestForm, ResetPasswordForm
from app.email import send_password_reset_email


# The before_request decorated from Flask register the decorated function to be executed
# right before the view function. This is extremely useful because we can insert code that
# we want to execute before any view function in the application, and we can have it in a
# single place.
@app.before_request
def before_request():
    # The implementation simply checks if the current_user is logged in, and in that case sets
    # the last_Seen field to the current time. We use UTC for consistent time units.
    # Using local time is not a good idea because it goes into the database depending on your
    # location.
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()

        # Commit the database session, so that the change made above is written to the database
        # There is no db.session.add() before commit, when we reference current_user, Flask Login
        # will invoke the user loader callback function which will run a db query that will put
        # the target user in the database session.
        db.session.commit()


# The two lines below are decorators. A decorators modifies the function as
# callbacks to certain events

# In our case the @app.route decorator creates an association between the URLs
# given as an argument and the function. There are two decorators, which associate
# URLs '/' and '/index' to this function. When a web browser requests either of
# these two URLs, Flash is going to invoke this function and pass the return value
# back to the browser as a response.

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    # Import post and postform classes
    form = PostForm()
    if form.validate_on_submit():
        # The template receives the form object as an argument
        # The author has its backref attribute set up in the models file.
        post = Post(body=form.post.data, author=current_user)
        # Inserts new Post record into the database
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')

    # Its necessary to redirect POST requests generated by web form submission with
    # a redirect. Helps mitigate the annoyance with how the refresh command is
    # implemented in web browsers. If POST request with a form submission returns
    # a regular response, then a refresh will re-submit the form.
    # If a POST is answered with a redirect, the browser is now instructed to send a
    # GET request to grab the page indicated in the redirect.
    # This simple trick is called Post/Redirect/Get pattern.
    page = request.args.get('page', 1, type=int)
    # Pagination is a method that can be called on any query object from Flask-SQLAlchemy
    # and it takes three arguments
    #  - The page number, starting from 1
    #  - The number of items per page
    #  - An error flag, if true then it would throw a 404 error and will return automatically
    #    to client. If false an empty list would be ereturned for out of range pages
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_next else None
    # # Calling all() on this query triggers its execution with the return value being
    # # a list with all the results.
    # posts = current_user.followed_posts().all()
    return render_template('index.html', title='Home', form=form, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


# The methods argument in the route decorator tells Flask that this view function
# accepts GET and POST requests, overriding the default which is GET. The HTTP protocol
# states that GET requests are those that return information to the client. All the
# POST requests are typically used when the browser submits form data to the server.
# By providing the methods argument, Flask is accepting POST and GET.
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    # This method does all the form processing work. When the browser sends the GET
    # request to receive the web page with the form, this method is going to return False.
    # When POST is sent as user is pressing submit button, this methods grabs all the data
    # runs validators and return True, meaning data is valid and can be processed.
    if form.validate_on_submit():
        # We now can log the user in for real. The first step is to load the user
        # from the database. The username came with the form submission, query the
        # db with that to find the user
        # We are using the filter_by() method of the SQLAlchemy query object. The result
        # of filter_by() method of SQLAlchemy that includes the objects that have a matching
        # username.
        # Since there is only going to be one or zero results, complete the query by calling
        # first(), which will return the user if object exists, or None if it does not.
        user = User.query.filter_by(username=form.username.data).first()

        # If got a match for the username that was provided, check if the password is
        # also valid. We invoke the check_password method defined in models. This will take
        # the password hash and determine whether if it matches the hash or not.
        # So now there are two error conditions, no username or incorrect password, flash a message
        # which redirects user back to the login prompt
        if user is None or not user.check_password(form.password.data):
            # Flash function is useful to show a message to user.
            # When you call a Flash() function, Flask stores the message, but not appear in web
            # pages. Need to add the messages in the base layout
            flash('Invalid username or password')
            return redirect(url_for('login'))

        # If username and password are both correct, then call the login_user() function,
        # which comes from Flask_Login. This function will register the user as logged in,
        # so that means any future pages that the user navigates to will have current_user
        # variable set to that user
        login_user(user, remember=form.remember_me)

        # Right after the user is logged in, the value of the next query string argument
        # is obtained. Flask provides a request variable that contains all the information
        # that the client sent with the request. In particular, the request.args attribute
        # exposes the contents of the query string in a friendly dictionary format.
        # There are three cases that needs to be considered to determine where to redirect
        # - If the login URL does not have a next argument, then the user is redirected to index
        # - If URL includes a next argument that is set to relative path, URL without domain portion,
        #   then the user is redirected to that URL
        # - If the login URL includes a argument that is set to a full URL that includes a domain
        #   name, then the user is redirected to the index page
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

        # This function tells the browser browser to automatically navigate to a different
    return render_template('login.html', title='Sign In', form=form)


@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Explore', posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


# There also need to offer users the option to log out of the application. Done with flask
# -login's logout_user() function.
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


# The decorator route this time has a dynamic component in it, which is indicated
# as the <username> URL component. When a route has a dynamic component, Flask will
# accept any text in that portion of the URL, and will invoke the view function with
# the actual text as an argument.
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, form=form)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))

    # If the browser sent a GET request, we need to respond by providing initial version of the
    # form template. It can also be when the browser sends a POST request with form data, but some
    # in that is invalid.
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format((username)))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot follow yourself!'.format((username)))
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('You are following {}!'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))


@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format((username)))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot un-follow yourself!'.format((username)))
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You are not following {}!'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    # This method will only return a token if its valid, or None if not
    user = User.verify_reset_password_token()
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html',form=form)
