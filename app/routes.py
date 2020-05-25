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

from flask import render_template, flash, redirect, url_for,request
from app import app
from app.forms import LoginForm
from flask_login import current_user, login_user, logout_user,login_required
from app.models import User
from werkzeug.urls import url_parse


# The two lines below are decorators. A decorators modifies the function as
# callbacks to certain events

# In our case the @app.route decorator creates an association between the URLs
# given as an argument and the function. There are two decorators, which associate
# URLs '/' and '/index' to this function. When a web browser requests either of
# these two URLs, Flash is going to invoke this function and pass the return value
# back to the browser as a response.

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username': 'Will'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'The Avengers movie was so cool!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'Its a beautiful day in Vancouver!!'
        },
    ]
    return render_template('index.html', title='Home Page', posts=posts)


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
        if user is None or user.check_password(form.password.data):
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
        # page, given as an argument.
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

# There also need to offer users the option to log out of the application. Done with flask
# -login's logout_user() function.
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
