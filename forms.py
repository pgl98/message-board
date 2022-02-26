from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Length

class ThreadForm(FlaskForm):
    title = StringField("Title:", validators=[InputRequired(), Length(min=1, max=255)])
    body = StringField("Body:", validators=[Length(min=0, max=5000)])
    submit = SubmitField("Submit")

class LoginForm(FlaskForm):
    username = StringField("Username:", validators=[InputRequired(), Length(min=1, max=100)])
    password = StringField("Password:", validators=[InputRequired()])
    submit = SubmitField("Log In")