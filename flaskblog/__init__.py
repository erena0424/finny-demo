from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flaskblog.config import Config
from flask_admin import Admin


db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    

    from flaskblog.users.routes import users
    from flaskblog.posts.routes import posts
    from flaskblog.main.routes import main
    from flaskblog.errors.handlers import errors
    #from flaskblog.recommendation.recommendation import recommendation
    
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)
    #to add recommendation system
    #app.register_blueprint(recommendation)

    """ 
    # to add admin view
    from flaskblog.models import User, Role, Post, Review, Category
    from flaskblog.users.adminviews import UserAdmin, RoleAdmin, PostAdmin, ReviewAdmin, CategoryAdmin
    admin = Admin(app, name='My Admin Panel', template_mode='bootstrap4')
    admin.add_view(UserAdmin(User, db.session))
    admin.add_view(RoleAdmin(Role, db.session))
    admin.add_view(PostAdmin(Post, db.session))
    admin.add_view(ReviewAdmin(Review, db.session))
    admin.add_view(CategoryAdmin(Category, db.session))
    admin.add_view(RatingAdmin(Rating, db.session)) 
    """

    from flaskblog.users.utils import is_admin, is_company, is_general
    from flaskblog.main.forms import SearchForm
    from flaskblog.models import Category
    @app.context_processor
    def base():
        role={"is_admin":is_admin, "is_company":is_company, "is_general":is_general}
        categories = Category.query.all()
        form = SearchForm()
        form.categories.choices = [(c.name) for c in categories]
        return dict(role=role, form=form)


    return app