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

from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm


# The two lines below are decorators. A decorators modifies the function as
# callbacks to certain events

# In our case the @app.route decorator creates an association between the URLs
# given as an argument and the function. There are two decorators, which associate
# URLs '/' and '/index' to this function. When a web browser requests either of
# these two URLs, Flash is going to invoke this function and pass the return value
# back to the browser as a response.

@app.route('/')
@app.route('/index')
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
    return render_template('index.html', title='Will', user=user, posts=posts)

# The methods argument in the route decorator tells Flask that this view function
# accepts GET and POST requests, overriding the default which is GET. The HTTP protocol
# states that GET requests are those that return information to the client. All the
# POST requests are typically used when the browser submits form data to the server.
# By providing the methods argument, Flask is accepting POST and GET.
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    # This method does all the form processing work. When the browser sends the GET
    # request to receive the web page with the form, this method is going to return False.
    # When POST is sent as user is pressing submit button, this methods grabs all the data
    # runs validators and return True, meaning data is valid and can be processed.
    if form.validate_on_submit():
        # Flash function is useful to show a message to user.
        # When you call a Flash() function, Flask stores the message, but not appear in web
        # pages. Need to add the messages in the base layout
        flash('Login requested for user {}, remember_me={},password={}'.format(
            form.username.data, form.remember_me.data,form.password.data))
        # This function tells the browser browser to automatically navigate to a different
        # page, given as an argument.
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)
