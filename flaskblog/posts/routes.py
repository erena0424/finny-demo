from flask import render_template, url_for, flash, redirect, request, abort, Blueprint, jsonify
from flaskblog import db
from flaskblog.posts.forms import PostForm, ReviewForm, CommentForm
from flaskblog.models import Post, Review, Category, Additional_image, Comment
from flask_login import current_user, login_required
from flaskblog.posts.utils import save_picture
from datetime import datetime
import pytz


posts = Blueprint('posts', __name__)

@posts.route("/post/new", methods=['GET','POST'])
@login_required
def new_post():
    categories = Category.query.all()
    form = PostForm() 
    form.categories.choices = [(c.name) for c in categories]
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user, website = form.website.data, app_store = form.app_store.data, google_play = form.google_play.data)
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            post.image_file = picture_file
            # db.session.commit()
        if form.additional_pictures.data and len(form.additional_pictures.data)>1:
            additional_picture_files = []
            for additional_picture in form.additional_pictures.data:
                additional_picture_file = save_picture(additional_picture)
                additional_picture_files.append(additional_picture_file)
            for filename in additional_picture_files:
                    additional_picture = Additional_image(image_file=filename, post_id=post.id)
                    db.session.add(additional_picture)
                    post.additional_images.append(additional_picture)
        if form.no_picture.data:
            post.image_file = None
            post.additional_images = []
        if form.categories.data:
            for category_name in form.categories.data:
                category = Category.query.filter_by(name=category_name).first()
                if category:  # Check if the category exists
                    post.categories.append(category)
        db.session.add(post)
        db.session.commit()
        flash('投稿しました!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title="New Post", form=form, legend='新規投稿')

@posts.route("/post/<int:post_id>", methods=['GET','POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    reviews = Review.query.filter_by(post=post)\
        .order_by(Review.date_reviewed.desc())\
        .paginate(page=page,per_page=5)
    form = ReviewForm()
    categories = Category.query.all()
    form.categories.choices = [(c.name) for c in categories]
    if form.validate_on_submit():
        if post_id:
            post = Post.query.get_or_404(post_id)
            if request.form.get('rating'):
                selected_rating = int(request.form.get('rating'))
                if post.ave_rating:
                    post.ave_rating=(post.ave_rating*len(post.reviews)+selected_rating)/(len(post.reviews)+1)
                else:
                    post.ave_rating=selected_rating/(len(post.reviews)+1)
            else:
                selected_rating = 0
            review = Review(title=form.title.data, content=form.content.data, is_in_timeline=form.is_in_timeline.data, user_id=current_user.id, post_id=post_id, rating=selected_rating, categories=post.categories)
            #review.ratings.append(Rating(name="rating", value=form.rating.data))
            db.session.add(review)
            db.session.commit()
            flash('レビューを投稿しました!', 'success')
            return redirect(url_for('posts.post',post_id=post_id))
    return render_template('post.html',title=post.title, post=post, reviews=reviews, form=form, legend='新規レビューを投稿する')


@posts.route("/post/<int:post_id>/update", methods=['GET','POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    categories = Category.query.all()
    form = PostForm() 
    form.categories.choices = [(c.name) for c in categories]
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.website = form.website.data
        post.app_store = form.app_store.data
        post.google_play = form.google_play.data
        if form.no_picture.data:
            post.image_file = None
            post.additional_images = []
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            post.image_file = picture_file
        if form.additional_pictures.data and any(form.additional_pictures.data)>0:
            additional_picture_files = []
            for additional_picture in form.additional_pictures.data:
                additional_picture_file = save_picture(additional_picture)
                additional_picture_files.append(additional_picture_file)
            for filename in additional_picture_files:
                    additional_picture = Additional_image(image_file=filename, post_id=post.id)
                    post.additional_images.append(additional_picture)
        if form.categories.data:
            post.categories = []
            for category_name in form.categories.data:
                category = Category.query.filter_by(name=category_name).first()
                if category:  # Check if the category exists
                    post.categories.append(category)
        db.session.commit()
        flash('投稿を更新しました!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.website.data = post.website
        form.app_store.data = post.app_store
        form.google_play.data = post.google_play
    return render_template('create_post.html',title='Update Post', form=form, legend='Update Post')

@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    reviews = Review.query.filter_by(post_id=post_id)
    for review in reviews:
        db.session.delete(review)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('投稿を削除しました', 'success')
    return redirect(url_for('main.home'))

@posts.route("/post/<int:post_id>/like", methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post in current_user.liked_posts:
        current_user.liked_posts.remove(post)
    else:
        current_user.liked_posts.append(post)
    db.session.commit()
    
    # Return a JSON response to indicate success
    return jsonify({'message': 'Success'})


@posts.route("/review/<int:review_id>", methods=['GET','POST'])
def review(review_id):
    review = Review.query.get_or_404(review_id)
    comments = Comment.query.filter_by(review_id=review.id)
    form=CommentForm()
    if form.validate_on_submit():
        print('okay')
        comment=Comment(comment=form.comment.data, user_id=current_user.id, review_id=review.id)
        db.session.add(comment)
        db.session.commit()
        flash('送信しました!', 'success')
        # Redirect to the same review page after posting a comment
        return redirect(url_for('posts.review', review_id=review.id))
    return render_template('review.html',title=review.title, review=review, comments=comments,form=form)

@posts.route("/post/new_review", methods=['GET','POST'])
@login_required
def new_review(post_id=None):
    form = ReviewForm()
    categories = Category.query.all()
    form.categories.choices = ["言語交換","記録・共有","指導・質問対応","資格・専門"]
    if form.validate_on_submit():
        if request.form.get('rating'):
            selected_rating = int(request.form.get('rating'))
        else:
            selected_rating = 0
        review = Review(title=form.title.data, content=form.content.data, is_in_timeline=True, reviewer=current_user, rating=selected_rating)
        if form.categories.data:
            for category_name in form.categories.data:
                category = Category.query.filter_by(name=category_name).first()
                if category:  # Check if the category exists
                    review.categories.append(category)
        db.session.add(review)
        db.session.commit()
        flash('レビューを投稿しました!', 'success')
        return redirect(url_for('main.timeline'))
    return render_template('create_review.html', title="New Review", form=form, legend='新規投稿', post_id=post_id)

@posts.route("/review/<int:review_id>/update", methods=['GET','POST'])
@login_required
def update_review(review_id):
    review = Review.query.get_or_404(review_id)
    categories = Category.query.all()
    if review.reviewer != current_user:
        abort(403)
    form = ReviewForm()
    form.categories.choices = [(c.name) for c in categories]
    # form.rating.choices=[0]
    # form.rating.default = '0'
    #form.rating.choices=[(str(i)) for i in range(1,6)]
    if form.validate_on_submit():
        review.title = form.title.data
        review.content = form.content.data
        review.date_reviewed = datetime.now(pytz.timezone("Asia/Tokyo"))
        if request.form.get('rating'):
            selected_rating = int(request.form.get('rating'))
            review.rating = selected_rating
        db.session.commit()
        flash('編集を保存しました!', 'success')
        return redirect(url_for('posts.review', review_id=review.id))
    elif request.method == 'GET':
        form.title.data = review.title
        form.content.data = review.content
    return render_template('create_review.html',title='Update Review', form=form, legend='編集')

@posts.route("/review/<int:review_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    if review.reviewer != current_user:
        abort(403)
    db.session.delete(review)
    db.session.commit()
    flash('投稿を削除しました', 'success')
    return redirect(url_for('main.timeline'))




  
