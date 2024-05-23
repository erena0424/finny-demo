from flask import render_template, url_for, flash, redirect, request, Blueprint
from flaskblog import db, bcrypt
from flaskblog.users.forms import (RegistrationForm, CompanyRegistrationForm, LoginForm, UpdateAccountForm, 
                             RequestResetForm, ResetPasswordForm)
from flaskblog.models import User, Company, Post, Review, Role
from flaskblog.main.utils import recommend_posts
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog.users.utils import save_picture, send_reset_email, is_company, is_general, is_admin
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_

users = Blueprint('users', __name__)

@users.route("/register",methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    form.gender.choices = ['男性','女性','その他・答えたくない']
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        role = Role.query.filter_by(name="General").first()
        if form.gender.data=='男性':
            gender=1
        elif form.gender.data=='女性':
            gender=-1
        else: 
            gender=0
        user = User(username=form.username.data, email=form.email.data, birthdate=form.birthdate.data, gender=gender, password=hashed_password, role=role.id)
        db.session.add(user)
        try:
            db.session.commit()
            flash(f'Your account has been created! You are now able to log in!','success')
        except SQLAlchemyError as e:
            # Handle the exception or print detailed error information
            print("SQLAlchemy Error:", str(e), user)
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)

@users.route("/company_register",methods=['GET','POST'])
def company_register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = CompanyRegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        role = Role.query.filter_by(name="Company").first()
        user = User(username=form.company_name.data, email=form.email.data, password=hashed_password, role=role.id)
        #user.role.append(role)
        db.session.add(user)
        user = User.query.filter_by(email=form.email.data).first()
        company = Company(staff_name=form.staff_name.data, hojin_bango=form.hojin_bango.data, user=user)
        db.session.add(company)
        try:
            db.session.commit()
            flash(f'Your account has been created! You are now able to log in!','success')
        except SQLAlchemyError as e:
            # Handle the exception or print detailed error information
            print("SQLAlchemy Error:", str(e), user)
        flash(f'Your account has been created! You are now able to log in!','success')
        return redirect(url_for('users.login'))
    return render_template('company_register.html', title='Register', form=form)

@users.route("/login", methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            # if is_general(current_user):
            #     current_user.recommended_posts=recommend_posts(current_user, 2)
            #     db.session.commit()
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@users.route("/user/<string:username>/edit", methods=['GET','POST'])
@login_required
def account(username):
    form = UpdateAccountForm()
    recommended_posts=current_user.recommended_posts
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!','success')
        return redirect(url_for('users.account', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static',filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@users.route("/user/<string:username>/posts")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    if is_company(user) or is_admin(user):
        posts = Post.query.filter_by(author=user)\
            .order_by(Post.date_posted.desc())\
            .paginate(page=page,per_page=5)
        review_page = request.args.get('review_page', 1, type=int)
        reviews = Review.query.filter(Review.post_id.in_([post.id for post in posts.items]))\
            .order_by(Review.date_reviewed.desc())\
            .paginate(page=review_page, per_page=5)
        return render_template('user_posts.html', user=user, posts=posts, reviews=reviews)
    if is_general(user):
        reviews = Review.query.filter_by(reviewer=user)\
        .order_by(Review.date_reviewed.desc())\
        .paginate(page=page,per_page=5)
        return render_template('user_reviews.html', user=user, reviews=reviews)
        

@users.route("/reset_password", methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@users.route("/reset_password/<token>", methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('user.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been update! You are now able to log in!','success')    
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

#Probably not used
@users.route("/<string:username>/home")
def user_reviews(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    reviews = Review.query.filter_by(reviewer=user)\
        .order_by(Review.date_reviewed.desc())\
        .paginate(page=page,per_page=5)
    return render_template('user_reviews.html', user=user, reviews=reviews)

@users.route("/user/<string:username>/liked_posts")
def user_liked_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    liked_post_ids = [post.id for post in current_user.liked_posts]
    liked_posts = Post.query.filter(Post.id.in_(liked_post_ids))\
            .order_by(Post.date_posted.desc())\
            .paginate(page=page,per_page=5)
    # for post in liked_posts:
    #     reviews = Review.query.filter_by(post=post)\
    #         .order_by(Review.date_reviewed.desc())\
    #         .paginate(page=page,per_page=5)
      # You can adjust the per_page value as needed
    reviews = Review.query.filter(Review.post_id.in_(liked_post_ids))\
        .order_by(Review.date_reviewed.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_liked_posts.html', posts=liked_posts, user=user, reviews=reviews)
   