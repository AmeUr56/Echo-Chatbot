from flask_login import UserMixin

from app import db

class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    google_id = db.Column(db.Integer,unique=True,nullable=True)
    name = db.Column(db.String(10),nullable=False)
    email = db.Column(db.String,unique=True,nullable=False)
    password = db.Column(db.String(),nullable=True)
    picture = db.Column(db.Boolean(),default=False)
    ip_address = db.Column(db.String,nullable=False)
    created_at = db.Column(db.DateTime,nullable=False)
    updated_at = db.Column(db.DateTime)

    @property
    def is_admin(self):
        return self.role and self.role.is_admin

    @property
    def is_super_admin(self):
        return self.role and self.role.is_super_admin
    
    # The relationship with Stats
    stats = db.relationship('Stats', uselist=False, backref='user',cascade='all, delete-orphan')
    
    # The relationship with Feedbacks
    feedback = db.relationship('Feedback', lazy=True, backref='user',cascade='all, delete-orphan')

    # The Relationship with Role
    role = db.relationship('Role', uselist=False, backref='user',cascade='all, delete-orphan')

    # The relationship with Discussion
    discussion = db.relationship('Discussion', lazy=True, backref='user',cascade='all, delete-orphan')

class Role(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    is_super_admin = db.Column(db.Boolean,default=False)
    is_admin = db.Column(db.Boolean,default=False)

    # Relationship Attribute
    user_id = db.Column(db.Integer, db.ForeignKey('user.id',ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

class Stats(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    length = db.Column(db.Integer,default=0)
    prompts = db.Column(db.Integer,default=0)
    last_at = db.Column(db.DateTime)
    
    # Relationship Attribute
    user_id = db.Column(db.Integer, db.ForeignKey('user.id',ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    
class Discussion(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    prompt = db.Column(db.String(500),nullable=False)
    response = db.Column(db.String(),nullable=False)
    index = db.Column(db.Integer,nullable=False)
    
    # Relationship Attribute
    user_id = db.Column(db.Integer,db.ForeignKey('user.id',ondelete='CASCADE', onupdate='CASCADE'),nullable=False)

class Feedback(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    opinion = db.Column(db.String(100),nullable=False)
    send_at = db.Column(db.DateTime)
    
    # Relationship Attribute
    user_id = db.Column(db.Integer, db.ForeignKey('user.id',ondelete='CASCADE', onupdate='CASCADE'),nullable=False)