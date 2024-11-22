from flask import Flask,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager,AnonymousUserMixin,current_user
from flask_admin import Admin
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_socketio import SocketIO
from authlib.integrations.flask_client import OAuth

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
socketio = SocketIO()
oauth = OAuth()

def create_app():
    app = Flask(__name__)
    load_dotenv()
    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
    app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET')
    app.config['CACHE_TYPE'] = "simple"
    
    # Link Initialized Extentions to the App
    db.init_app(app)
    migrate.init_app(app,db)
    bcrypt.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    socketio.init_app(app)
    oauth.init_app(app)
    #-----------------------Login Manager-----------------------#
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

        @property
        def google_id(self):
            return 0
        
    # Set the custom AnonymousUser class
    login_manager.anonymous_user = AnonymousUser
    #---------------------------------------------------------#

    #-----------------------Admin Panel-----------------------#
    # Import Models,Views
    from models import User,Feedback,Role,Stats,Discussion
    from views import UserModelView,RoleModelView,StatsModelView,FeedbackModelView,DiscussionModelView,ProfilePicturesView,FeaturesView,DashboardView

    # Initialize Flask-Admin instance
    admin = Admin(app, name='Admin', template_mode='bootstrap3', index_view=DashboardView(name='Dashboard',endpoint=""))
    
    # Link Each View to a Model
    admin.add_view(UserModelView(User, db.session))
    admin.add_view(RoleModelView(Role, db.session))
    admin.add_view(StatsModelView(Stats, db.session))
    admin.add_view(FeedbackModelView(Feedback, db.session))
    admin.add_view(DiscussionModelView(Discussion, db.session))
    admin.add_view(ProfilePicturesView(name='ProfilePictures',endpoint="pfps"))
    admin.add_view(FeaturesView(name='Features',endpoint="features"))
    #----------------------------------------------------------#

    #-----------------------OAuth-----------------------#
    google = oauth.register(
        name='google',
        client_id = app.config['GOOGLE_CLIENT_ID'],
        client_secret = app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={'scope':'openid profile email'}
    )
    #----------------------------------------------------#
    
    # Link Endpoints to the app
    from routes import register_routes
    register_routes(app,db,bcrypt,limiter,cache,socketio,google)
    
    return app