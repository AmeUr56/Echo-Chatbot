from flask import Flask,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager,AnonymousUserMixin,current_user
from flask_admin import Admin,AdminIndexView,BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

import os
from dotenv import load_dotenv

# Initialize Extentions
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
csrf = CSRFProtect()
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address)
cache = Cache()

def create_app():
    app = Flask(__name__)
    load_dotenv()
    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    
    # Link Initialized Extentions to the App
    db.init_app(app)
    migrate.init_app(app,db)
    bcrypt.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    #-----------------------Login Manger-----------------------#
    login_manager.init_app(app)
    
    # Redirect to it if not logged in
    login_manager.login_view = 'login'

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Handle Users Attributes for Anonymous ones
    class AnonymousUser(AnonymousUserMixin):
        @property
        def id(self):
            return False
        
        @property
        def is_admin(self):
            return False

        @property
        def is_super_admin(self):
            return False
            
        @property
        def picture(self):
            return False

    # Set the custom AnonymousUser class
    login_manager.anonymous_user = AnonymousUser

    #----------------------------------------------------------#

    #-----------------------Admin Panel-----------------------#
    # Admin Panel
    class MyAdminIndexView(AdminIndexView):
        def is_accessible(self):
            return current_user.is_admin

        def inaccessible_callback(self, name, **kwargs):
            return redirect(url_for('index'))
    
    # Initialize Flask-Admin instance
    admin = Admin(app, name='Admin', template_mode='bootstrap3', index_view=MyAdminIndexView())

    # Add views for each model
    class UserModelView(ModelView):
        column_display_fk = True
        column_list = ['id','is_admin','name','picture','email','password','ip_address','created_at','updated_at']

        def is_accessible(self):
            return current_user.is_admin

        def inaccessible_callback(self, name, **kwargs):
            return redirect(url_for('/admin'))
        
    class RoleModelView(ModelView):
        column_display_fk = True
        column_list = ['id','user_id','is_super_admin','is_admin']

        def is_accessible(self):
            return current_user.is_super_admin

        def inaccessible_callback(self, name, **kwargs):
            return redirect(url_for('/admin'))
    
    class DiscussionModelView(ModelView):        
        column_display_fk = True
        column_list = ['id','user_id','length','time','last_at']

        def is_accessible(self):
            return current_user.is_admin

        def inaccessible_callback(self, name, **kwargs):
            return redirect(url_for('/admin'))
        
    class FeedbackModelView(ModelView):
        column_display_fk = True
        column_list = ['id','user_id','opinion','send_at']

        def is_accessible(self):
            return current_user.is_admin

        def inaccessible_callback(self, name, **kwargs):
            return redirect(url_for('/admin'))
    
    from models import User,Discussion,Feedback,Role
    admin.add_view(UserModelView(User, db.session))
    admin.add_view(RoleModelView(Role, db.session))
    admin.add_view(DiscussionModelView(Discussion, db.session))
    admin.add_view(FeedbackModelView(Feedback, db.session))
    #----------------------------------------------------------#

    # Link Endpoints to the app
    from routes import register_routes
    register_routes(app,db,bcrypt,limiter,cache)
    
    return app