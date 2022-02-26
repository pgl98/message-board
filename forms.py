from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Length

class ThreadForm(FlaskForm):
    title = StringField("Title:", validators=[InputRequired(), Length(min=1, max=250)])
    body = StringField("Body:", validators=[Length(min=0, max=5000)])
    submit = SubmitField("Submit")