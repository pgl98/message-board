from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
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