#-------------------------------------------------------------------------------
# File Name: Routes.py
#
# Purpose:
# The routes are the different URLS that the application implements. Handlers of
# for the application routes are written as Python Functions, called view
# functions. View functions are mapped to one or more route URLs so that Flask
# knows what logic to execute when a client requests a given URL
#-------------------------------------------------------------------------------

from app import app

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
    return 'Hello World!'