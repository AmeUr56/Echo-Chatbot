from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from redis import Redis
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import os
from dotenv import load_dotenv

# Initialize Extentions
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
csrf = CSRFProtect()
login_manager = LoginManager()

redis = Redis(host='localhost', port=6379, db=0)
limiter = Limiter(key_func=get_remote_address,storage_uri='redis://localhost:6379',)

def create_app():
    app = Flask(__name__)
    load_dotenv()
    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')

    # Link Initialized Extensitons to the App
    db.init_app(app)
    migrate.init_app(app,db)
    bcrypt.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    #-----------------------Login Manger-----------------------#
    login_manager.init_app(app)
    
    # Redirect to it if not logged in
    login_manager.login_view = 'login'

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    #----------------------------------------------------------#

    #-----------------------Admin Panel-----------------------#
    # Create Flask-Admin instance    
    from routes import MyAdminIndexView
    admin = Admin(app, name='Admin', template_mode='bootstrap3', index_view=MyAdminIndexView())
    
    # Add views for each model
    from models import User,Discussion,Feedback
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Discussion, db.session))
    admin.add_view(ModelView(Feedback, db.session))
    #----------------------------------------------------------#

    from routes import register_routes
    register_routes(app,db,bcrypt,limiter)
    
    return app