import os 

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'  # Use environment variable
    MAIL_SERVER= 'smtp.googlemail.com' 
    MAIL_PORT=  # Add mail port
    MAIL_USE_TLS = True
    MAIL_USERNAME = '' # Add the email address to send the password reset email
    MAIL_PASSWORD = '' # Add the password to allow this app to send the email, if needed

