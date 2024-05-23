from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flaskblog.models import Role


class AdminModelView(ModelView):
    def is_accessible(self):
        role = Role.query.filter_by(name='Admin').first()
        return True
        #return current_user.is_authenticated and current_user.role == role
class UserAdmin(AdminModelView):
    column_list = ('username', 'email', 'role')
    column_labels = {'username': 'Username', 'email': 'Email Address', 'role': 'Role'}
    column_filters = ('username', 'email', 'role.name')

class RoleAdmin(AdminModelView):
    column_list = ('name',)
    column_labels = {'name': 'Role Name'}
    column_filters = ('name',)

class PostAdmin(AdminModelView):
    column_list = ('title', 'author', 'content', 'category')
    column_labels = {'title': 'Post Title', 'author': 'Author', 'content': 'Content', 'category':'Category'}
    column_filters = ('title', 'author.username', 'content', 'categories.name')

class ReviewAdmin(AdminModelView):
    column_list = ('title', 'author', 'content', 'rating')
    column_labels = {'title': 'Review Title', 'author': 'Author', 'content': 'Content', 'rating':'Rating'}
    column_filters = ('title', 'reviewer.username', 'content', 'rating')

class CategoryAdmin(AdminModelView):
    column_list = ('name',) # Notice the comma after 'name'
    column_labels = {'name': 'Category Name'}
    column_filters = ('name',)

# class RatingAdmin(AdminModelView):
#     column_list = ('name', 'value') # Notice the comma after 'name'
#     column_labels = {'name': 'CategoryRating Name', 'value':'Value'}
#     column_filters = ('name', 'value')