from datetime import datetime
import pytz
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from flaskblog import db, login_manager
from flask_login import UserMixin
from flask import current_app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
def get_jst_now():
  return datetime.now(pytz.timezone("Asia/Tokyo"))
recommended_posts = db.Table('recommended_posts',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True)
)

likes = db.Table('user_post',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True)
)
post_category = db.Table('post_category',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)
review_category = db.Table('review_category',
    db.Column('review_id', db.Integer, db.ForeignKey('review.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)
# if we need various ratings
# review_rating = db.Table('review_rating',
#     db.Column('review_id', db.Integer, db.ForeignKey('review.id'), primary_key=True),
#     db.Column('rating_id', db.Integer, db.ForeignKey('rating.id'), primary_key=True)
# )

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    #role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    #role = db.relationship('Role', backref=db.backref('users', lazy=True)) #,secondary='user_roles',
    role = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    birthdate = db.Column(db.Date)
    age = db.Column(db.Integer)
    gender = db.Column(db.String)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete')
    recommended_posts = db.relationship(
        'Post',
        secondary=recommended_posts,
        lazy=True,
        backref=db.backref('recommended_to', lazy=True)
    )
    reviews = db.relationship('Review', backref='reviewer', lazy=True)
    comments = db.relationship('Comment', backref='commenter', lazy=True)
    company = db.relationship('Company', backref='user', lazy=True)
    liked_posts = db.relationship('Post', secondary=likes, lazy=True, back_populates='liked_users', overlaps="author,posts")
    
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})
    
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)
   
    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.image_file}','{self.company}','{self.role}')"

class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"Role('{self.name}')"

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staff_name = db.Column(db.String(20),nullable=False)
    hojin_bango = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f"Role('{self.staff_name}','{self.hojin_bango}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100),nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=get_jst_now)
    content = db.Column(db.Text)
    image_file = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reviews= db.relationship('Review', backref='post', lazy=True)
    ave_rating = db.Column(db.Integer)
    categories = db.relationship('Category', secondary=post_category, backref='posts')#backref=db.backref('posts', lazy=True), lazy='dynamic', secondaryjoin=(id == categories.c.post_id)
    additional_images = db.relationship('Additional_image', cascade="all,delete", backref='post', lazy=True)
    website = db.Column(db.String)
    app_store = db.Column(db.String)
    google_play = db.Column(db.String)
    liked_users = db.relationship('User', secondary=likes, lazy=True, back_populates='liked_posts', overlaps="author,posts")

    def __repr__(self):
        return f"Post('{self.title}','{self.date_posted}','{self.content}',{self.image_file}','{self.user_id}','{self.reviews}')"
class Additional_image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_file = db.Column(db.String(20), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    date_reviewed = db.Column(db.DateTime, nullable=False, default=get_jst_now)
    content = db.Column(db.Text)
    rating = db.Column(db.Integer)
    image_file = db.Column(db.String(20), default='post_default.png')
    is_in_timeline = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    categories= db.relationship('Category', secondary=review_category, backref='reviews')
    #if we need various ratings
    #ratings = db.relationship('Rating', secondary=review_rating, backref='reviews') # backref=db.backref('review', lazy=True), lazy='dynamic', secondaryjoin=(id == ratings.c.review_id)
    
    
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    
    def __repr__(self):
        return f"Category('{self.name}')"

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_commented = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone("Asia/Tokyo")))
    comment = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey('review.id'))
    
