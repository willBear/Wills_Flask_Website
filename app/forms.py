from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
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

    # When you add any methods that match the pattern validate_<field_name>
    # WTForms take those as custom validators and invokes them in addition to
    # stock validators. In the event a result exists, a validation error is
    # triggered by raising ValidationError. The message included as the argument
    # in the exception will be the message that will be displayed next to the field
    # for the user to see

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address')

# We are using a new field type and a new validator in this form. For the 'about'
# field we use a TextAreaField, which is a multi-line box in which the user can
# enter text. To validate the field we would use Length. Which will make sure that
# the text entered is between 0 and 140 characters.
class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')