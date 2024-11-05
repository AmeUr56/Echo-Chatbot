from app import db
from flask_login import UserMixin

class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    is_admin = db.Column(db.Boolean,default=False)
    name = db.Column(db.String(10),nullable=False)
    email = db.Column(db.String,unique=True,nullable=False)
    password = db.Column(db.String(30),nullable=False)
    profile_picture = db.Column(db.BLOB, nullable=True)
    ip_address = db.Column(db.String,nullable=False,unique=True)
    created_at = db.Column(db.DateTime,nullable=False)
    updated_at = db.Column(db.DateTime)
    
    # The relationship with Discussions
    discussion = db.relationship('Discussion', uselist=False, backref='user')
    
    # The relationship with Feedbacks
    feedback = db.relationship('Feedback', lazy=True, backref='user')

class Discussion(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    length = db.Column(db.Integer,default=0)
    time = db.Column(db.Integer,default=0)
    last_at = db.Column(db.DateTime)
    
    # Relationship Attribute
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    
class Feedback(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    opinion = db.Column(db.String(100),nullable=False)
    send_at = db.Column(db.DateTime)
    
    # Relationship Attribute
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
