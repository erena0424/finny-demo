from flaskblog import db
from run import app
app.app_context().push()
db.create_all()