from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Optional


class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[DataRequired()])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class CsrfOnlyForm(FlaskForm):
    """ CSRF form """

class EditUserForm(FlaskForm):
    """Form for editing users."""

    username = StringField('Username')
    email = StringField('E-mail', validators=[Optional(),Email()])
    image_url = StringField('Image url')
    header_image_url = StringField('(Optional) Image URL')
    bio = TextAreaField()
    password = PasswordField('Password', validators=[Length(min=6)])



