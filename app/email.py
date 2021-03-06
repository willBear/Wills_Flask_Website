from flask_mail import Message
from flask import render_template
from app import mail, app

# Now we implement threading to reduce processing time of sending out emails,
# this is achieved by sending out threading
from threading import Thread

# The send async email function runs in the a back ground thread invoked via
# the Thread() class in the last line of send_mail().
# We also need to send the application instance, and flask uses flask context
# avoid having to pass arguments across functions. There are application contexts
# and request context. These contexts are automatically managed by the framework.
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg).start())


# Email is generated from templates using the familiar render_template() function.
# The templates receive the user and the token as arguments, and personalized email
# can be generated.

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Wills Website] Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))
