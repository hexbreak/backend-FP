import os
from flask_admin import Admin
from models import db, User, Platform, Backlog, GenreLike, GenreDislike, TagLike, TagDislike
from flask_admin.contrib.sqla import ModelView

def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='4Geeks Admin', template_mode='bootstrap3')

    
    # Add your models here, for example this is how we add a the User model to the admin
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Platform, db.session))
    admin.add_view(ModelView(Backlog, db.session))
    admin.add_view(ModelView(GenreLike, db.session))
    admin.add_view(ModelView(GenreDislike, db.session))
    admin.add_view(ModelView(TagLike, db.session))
    admin.add_view(ModelView(TagDislike, db.session))

    # You can duplicate that line to add mew models
    # admin.add_view(ModelView(YourModelName, db.session))