from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from app.models import User


# Most flask extensions use a flask_<name> naming convention for their top
# level import symbol. In this case, Flask-WTF has all its symbols under
# flask_wtf. This is where the FlaskForms base class is imported at the
# top of app/forms.py


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
    """
    When you add any methods that match the pattern validate_<field_name> 
    WTForms take those as custom validators and invokes them in addition to
    stock validators. In the event a result exists, a validation error is 
    triggered by raising ValidationError. The message included as the argument
    in the exception will be the message that will be displayed next to the field
    for the user to see 
    """
    def validate_self(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address')
