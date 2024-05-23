from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog.models import User
import requests
import xml.etree.ElementTree as ET
import urllib.parse

class RegistrationForm(FlaskForm):
    username = StringField('ユーザー名', 
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Eメール',
                        validators=[DataRequired(),Email()])   
    birthdate = DateField('生年月日', validators=[DataRequired()])
    gender = SelectField('性別', validators=[DataRequired()])
    password = PasswordField('パスワード', validators=[DataRequired()])
    confirm_password = PasswordField('パスワード（確認）', 
                                      validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('会員登録する')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('このユーザー名は既に使用されています')
    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('このメールアドレスは既に使用されています')
        
class CompanyRegistrationForm(FlaskForm):
    company_name = StringField('会社名', 
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Eメール',
                        validators=[DataRequired(), Email()]) 
    staff_name = StringField('担当者氏名', validators=[DataRequired(), Length(min=2, max=20)])
    hojin_bango =  StringField('法人番号', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('パスワード', validators=[DataRequired()])
    confirm_password = PasswordField('パスワード（確認）', 
                                      validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('会員登録する')
    def validate_username(self, company_name):
        user = User.query.filter_by(username=company_name.data).first()
        if user:
            raise ValidationError('この会社名は既に使用されています')
    def validate_email(self, email):
        print(email)
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('このメールアドレスは既に使用されています')
            
        
    
    # def validate_hojin_bango(self, hojin_bango):
    #     company_name = self.company_name.data
        
    #     # UTF-8でURLエンコード
    #     encoded_company_name = urllib.parse.quote(company_name, encoding='utf-8')
    #     # APIからXMLデータを取得
    #     response = requests.get(f'https://api.houjin-bangou.nta.go.jp/4/name?id=KFvmuH5gQrV6z&&name={encoded_company_name}&type=12')
    #     xml_data = response.text

    #     # XMLデータを解析
    #     root = ET.fromstring(xml_data)
        
    #     # 法人番号を取得
    #     corporate_numbers = []

    #     for corporation in root.findall(".//corporation"):
    #         corporate_number = corporation.find("corporateNumber").text
    #         corporate_numbers.append(corporate_number)
    #     print(corporate_numbers)
    #     print(hojin_bango.data)
    #     if (hojin_bango.data!=corporate_numbers[0]):
    #         raise ValidationError('法人番号が法人名と一致しません。')
        
class LoginForm(FlaskForm):
    email = StringField('メールアドレス',
                        validators=[DataRequired(),Email()])   
    password = PasswordField('パスワード', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('ログイン')

class UpdateAccountForm(FlaskForm):
    username = StringField('ユーザー名', 
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('メールアドレス',
                        validators=[DataRequired(),Email()])   
    picture = FileField('プロフィール画像を編集', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('変更を保存')
    
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('このユーザー名は既に使用されています')
        
    def validate_email(self, email):
        if email.data != current_user.email:
            email = User.query.filter_by(email=email.data).first()
            if email:
                raise ValidationError('このメールアドレスは既に使用されています')

class RequestResetForm(FlaskForm):
    email = StringField('メールアドレス',
                        validators=[DataRequired(),Email()])   
    submit = SubmitField('パスワードをリセット')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()

        if user is None:
            raise ValidationError('このメールアドレスは登録されていません')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('パスワード', validators=[DataRequired()])
    confirm_password = PasswordField('確認', 
                                      validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('パスワードをリセット')