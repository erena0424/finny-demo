from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, SelectMultipleField, BooleanField, URLField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileAllowed
#from flaskblog.models import Rating
from wtforms.fields import MultipleFileField

class PostForm(FlaskForm):
    title = StringField('タイトル', validators=[DataRequired()])
    content = TextAreaField('投稿内容')
    website = URLField('サイトのURL')
    app_store = URLField('app storeのURL')
    google_play = URLField('google playのURL')
    picture = FileField('カバー画像を選択', validators=[FileAllowed(['jpg', 'png'])])
    additional_pictures = MultipleFileField('写真を追加する', validators=[FileAllowed(['jpg', 'png'])])
    no_picture = BooleanField('画像を選択しない')
    categories  = SelectMultipleField('カテゴリー')
    submit = SubmitField('投稿する')

class ReviewForm(FlaskForm):
    title = StringField('タイトル', validators=[Length(max=100)])
    content = TextAreaField('投稿内容')
    picture = FileField('画像', validators=[FileAllowed(['jpg', 'png'])])
    # rating = SelectField('満足度')
    categories  = SelectMultipleField('カテゴリー') #, choices=[(str(i)) for i in range(1,6)]
    is_in_timeline = BooleanField('タイムラインにも投稿する')
    submit = SubmitField('投稿する')

class CommentForm(FlaskForm):
    comment = TextAreaField('コメント', validators=[DataRequired()])
    submit = SubmitField('送信')
