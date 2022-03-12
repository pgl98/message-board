from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField, RadioField
from flask_wtf.file import FileField # FileField is the Flask-WTF field for files
from wtforms.validators import InputRequired, Length, EqualTo

class ThreadForm(FlaskForm):
    title = StringField("Title:", validators=[InputRequired(), Length(max=255)])
    body = StringField("Body:", validators=[Length(min=0, max=5000)])
    submit = SubmitField("Create Thread")

class RegisterForm(FlaskForm):
    username = StringField("Username:", validators=[InputRequired(), Length(max=100)])
    password = PasswordField("Password:", validators=[InputRequired()])
    confirm_password = PasswordField("Confirm Password:", validators=[InputRequired(), EqualTo("password")])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    username = StringField("Username:", validators=[InputRequired(), Length(max=100)])
    password = PasswordField("Password:", validators=[InputRequired()])
    submit = SubmitField("Log In")

class CommentForm(FlaskForm):
    body = StringField("Comment:", validators=[InputRequired(), Length(max=5000)])
    submit = SubmitField("Post Comment")

class DeleteForm(FlaskForm):
    id = HiddenField(validators=[InputRequired()])
    submit = SubmitField("Delete")
    

# create the class
class UserProfileForm(FlaskForm):
    username = HiddenField()
    profile_image = FileField()
    about = StringField("About")
    submit = SubmitField("Confirm Edit")