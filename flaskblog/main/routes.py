from flask import render_template,request
from flaskblog.models import User, Post, Review, Category
from flaskblog.main.utils import recommend_posts
from flask import Blueprint
from flaskblog.main.forms import SearchForm, SearchReviewForm
from flask_login import current_user, login_required
from sqlalchemy import or_, and_, func
import pandas as pd



main = Blueprint('main', __name__)
# to use the recommendation system
# @login_required
# @main.route("/recommend")
# def recommendation():
#     # find the 10 most similar users to the current_user 
#     # while num_users < 10:
#     #   Database query filter age and gender to get more users 
#     #   add the query result to the users array and increment num_users
#     # call the functions from recommendation.py with the users array as input
#     # User.query.filter() --> filter for users within +/- 10 or 5 years away from the age of current_user.age
#     # once you have the list of user objects, reformat the list of objects into the right data structure to be fed into recommendation.py
#     sym_users = User.query.filter(and_(current_user.age - 5 < User.age, User.age < current_user.age - 5, User.gender==current_user.gender)).limit(10).all()
#     posts = Post.query.all() #get all posts

#     i = 2
#     while len(sym_users) < 10:
#         i += 1
#         sym_users = User.query.filter(and_(current_user.age - 5*i < User.age, User.age < current_user.age - 5*i, User.gender==current_user.gender)).limit(10).all()
#     sym_users = pd.DataFrame([{'gender': user.gender, 'age': user.age} for user in sym_users])

#     ratings_dict = {}
#     # Loop through users and posts to populate the ratings
#     for user in sym_users:
#         ratings_dict[user.username] = []
#         for post in posts:
#             # Replace this with the actual way you fetch ratings from your database
#             rating = 0  # You need to fetch the rating for the user and post here
#             ratings_dict[user.username].append(rating)

#     # Create the DataFrame
#     posts = pd.DataFrame(ratings_dict, index=[f'post_{i}' for i in range(len(posts))])
   
#     # recommended_posts_by_user= recommend_posts_by_user(current_user.id, 3, sym_users, posts) #get recommended posts based on symmilar users of the current user

    
#     return None

@main.route("/")
@main.route("/home", methods=['POST','GET'])
@main.route("/home/<string:category>", methods=['POST','GET'])
def home(category=None):
    page = request.args.get('page', 1, type=int)
    if current_user.is_authenticated:
        recommended_posts=current_user.recommended_posts
    else:
        recommended_posts=None
    
    posts = Post.query.order_by(Post.date_posted.desc())
    categories = Category.query.all()
    form = SearchForm()
    form.categories.choices = [(c.name) for c in categories]
   
    key_words = form.key_words.data
    selected_categories = form.categories.data

        
    if key_words or selected_categories:
        if key_words:
            # Split the entered keywords into a list
            keywords_list = key_words.split()
            # Create a list of filter conditions for each keyword
            # keyword_filters = [or_(Post.content.like('%' + keyword + '%'), Post.title.like('%' + keyword + '%')) for keyword in keywords_list]
            keyword_filters = [
                or_(
                    func.lower(Post.content).like(func.lower('%' + keyword + '%')),
                    func.lower(Post.title).like(func.lower('%' + keyword + '%'))
                ) for keyword in keywords_list
            ]
            if selected_categories:
                categories_to_filter = [Category.query.filter_by(name=category_name).first() for category_name in form.categories.data]
                posts = posts.filter(or_(*[Post.categories.contains(category) for category in categories_to_filter]))
            
            # Apply the keyword filters and paginate the results
            posts = posts.filter(or_(*keyword_filters)).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
        elif selected_categories:
            # If no keywords are provided, but selected categories are, filter by categories
            categories_to_filter = [Category.query.filter_by(name=category_name).first() for category_name in form.categories.data]
            posts = posts.filter(or_(*[Post.categories.contains(category) for category in categories_to_filter])).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
        
        return render_template('home.html', posts=posts, form=form, key_words=key_words, categories=selected_categories, recommended_posts=recommended_posts)
    elif category:
        category_to_filter= Category.query.filter_by(name=category).first() 
        posts = posts.filter(Post.categories.contains(category_to_filter)).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
        return render_template('home.html', posts=posts, form=form, key_words=None, categories=[category], recommended_posts=recommended_posts)
    
    # If neither keywords nor categories are provided, paginate all posts and render the home template
    posts = posts.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts, form=form, key_words=None, categories=None, recommended_posts=recommended_posts)

@main.route("/about")
def about():
    return render_template('about.html', title='About')

@main.route("/timeline", methods=['POST','GET'])
@main.route("/timeline/<string:category>", methods=['POST','GET'])
def timeline(category=None):
    
    page = request.args.get('page', 1, type=int)
    reviews = Review.query.filter(Review.is_in_timeline).order_by(Review.date_reviewed.desc())
    form = SearchReviewForm()
    categories = Category.query.all()
    form = SearchForm()
    form.categories.choices = [(c.name) for c in categories]

    key_words = form.key_words.data
    selected_categories = form.categories.data

    if key_words or selected_categories:
        if key_words:
            # Split the entered keywords into a list
            keywords_list = key_words.split()
            # Create a list of filter conditions for each keyword
            keyword_filters = [Review.content.like('%' + keyword + '%') for keyword in keywords_list]
            
            if selected_categories:
                categories_to_filter = [Category.query.filter_by(name=category_name).first() for category_name in form.categories.data]
                reviews = reviews.filter(or_(*[Review.categories.contains(category) for category in categories_to_filter]))
            
            # Apply the keyword filters and paginate the results
            reviews = reviews.filter(or_(*keyword_filters)).order_by(Review.date_reviewed.desc()).paginate(page=page, per_page=5)
        elif selected_categories:
            # If no keywords are provided, but selected categories are, filter by categories
            categories_to_filter = [Category.query.filter_by(name=category_name).first() for category_name in form.categories.data]
            reviews = reviews.filter(or_(*[Review.categories.contains(category) for category in categories_to_filter])).order_by(Review.date_reviewed.desc()).paginate(page=page, per_page=5)
        
        return render_template('timeline.html', reviews=reviews, form=form, key_words=key_words, categories=selected_categories)
    elif category:
            category_to_filter= Category.query.filter_by(name=category).first() 
            reviews = reviews.filter(Review.categories.contains(category_to_filter)).order_by(Review.date_reviewed.desc()).paginate(page=page, per_page=5)
            return render_template('timeline.html', reviews=reviews, form=form, key_words=None, categories=[category])
        
    # If neither keywords nor categories are provided, paginate all reviews and render the home template
    reviews = reviews.paginate(page=page, per_page=5)
    return render_template('timeline.html', reviews=reviews, form=form, key_words=None, categories=None)

