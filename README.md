demonstration video:
https://www.awesomescreenshot.com/video/26248843?key=3c405a7d16cf6d2557a487cd7b997418



## Configuration

This project requires some configuration settings to be set as environment variables. Here are the necessary settings:

- `SECRET_KEY`: A secret key for your application.
- `DATABASE_URL`: The database URL for SQLAlchemy.

Please add the environment variables or edit flaskblog/config.py to set these variables.

Additionally, I added add_user.py under the migrations folder for reference. If you need to alter the database after creating it, please make a new migration.