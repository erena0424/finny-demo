from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
    key_words = StringField('Key_words', validators=[DataRequired()])
    categories  = SelectMultipleField('Category')
    submit = SubmitField('Post')

class SearchReviewForm(FlaskForm):
    key_words = StringField('Key_words', validators=[DataRequired()])
    categories  = SelectMultipleField('Category')
    submit = SubmitField('Review')
