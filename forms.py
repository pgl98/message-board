from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Length

class ThreadForm(FlaskForm):
    title = StringField("Title:", validators=[InputRequired(), Length(max=255)])
    body = StringField("Body:", validators=[Length(min=0, max=5000)])
    submit = SubmitField("Create Thread")

class RegisterForm(FlaskForm):
    username = StringField("Username:", validators=[InputRequired(), Length(max=100)])
    password = StringField("Password:", validators=[InputRequired()])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    username = StringField("Username:", validators=[InputRequired(), Length(max=100)])
    password = StringField("Password:", validators=[InputRequired()])
    submit = SubmitField("Log In")

class CommentForm(FlaskForm):
    body = StringField("Comment:", validators=[InputRequired(), Length(max=5000)])
    submit = SubmitField("Post Comment")