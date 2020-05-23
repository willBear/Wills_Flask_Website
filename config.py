import os

# The configuration settings are defined as class variables inside the config
# class. As the application needs more configuration items, they can be added
# to this class, and later if theres need to have more than one configuration
# set, create subclasses to it.

# The SECRET_KEY configuration variable as the only configuration item is an
# important part in most Flask Applications. Flask and some of its extensions
# use the value of the secret key as a cryptographic key, useful to generate
# signatures or tokens.

# Flask WTF extension uses it to protect web forms against nasty attacks called
# Cross-Site Request Forgery.
class Config(object):
    # The value of the secret key is set as an expression with two terms, joined
    # by the or operator. The first term looks for the value of an environment
    # variable, and the second is just a hardcoded string.
    # The value sourced from an environment variable is preferred, but if the
    # environment does not defined the variable, then the hardcoded string is used

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'