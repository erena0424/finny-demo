import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flaskblog import mail
from flask_mail import Message
from flaskblog.models import Role

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
    
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)
    
    return picture_fn 

# def send_reset_email(user):
#     token = user.get_reset_token()
#     msg = Message('Password Reset Request', sender='noreply@gmail.com', recipients=[user.email])
#     msg.body = f'''To reset your password, visit the following link:
# {url_for('users.reset_token', token=token, _external=True)}

# このメールにお心当たりのない場合はメールを破棄していただきますようお願いいたします。
# '''
#     mail.send(msg)

def send_reset_email(user):
    token = user.get_reset_token()
    msg_title = "パスワードリセット"
    sender ='noreply@gmail.com'
    msg = Message(subject=msg_title, sender='noreply@demo.com', recipients=[user.email])
    msg_body = "このメールにお心当たりのない場合はメールを破棄していただきますようお願いいたします。"
    msg.body = f"""こちらのリンクからパスワードのリセットを行ってください
    {url_for('users.reset_token', token=token, _external=True)}

    このメールにお心当たりのない場合はメールを破棄していただきますようお願いいたします。
    """
    # data = {
    #     'app_name' : "REBWAE AI",
    #     'title' : msg_title,
    #     'body': msg_body,
    # }
    
    # msg.html = url_for('users.reset_token', token=data)
    try:
        mail.send(msg)
        return "Email sent..."
    except Exception as e:
        print(e)
        return "the email was not sent"
def is_admin(user):
    role = Role.query.filter_by(name="Admin").first()
    return user.role==role.id
def is_company(user):
    role = Role.query.filter_by(name="Company").first()
    return user.role==role.id
def is_general(user):
    role = Role.query.filter_by(name="General").first()
    return user.role==role.id