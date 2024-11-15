from flask_login import UserMixin

from app import db

class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(10),nullable=False)
    email = db.Column(db.String,unique=True,nullable=False)
    password = db.Column(db.String(),nullable=False)
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
    
    # The relationship with Discussions
    discussion = db.relationship('Discussion', uselist=False, backref='user')
    
    # The relationship with Feedbacks
    feedback = db.relationship('Feedback', lazy=True, backref='user')

    # Relationship with Role
    role = db.relationship('Role', uselist=False, backref='user')

class Role(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    is_super_admin = db.Column(db.Boolean,default=False)
    is_admin = db.Column(db.Boolean,default=False)

    # Relationship Attribute
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Discussion(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    length = db.Column(db.Integer,default=0)
    time = db.Column(db.Integer,default=0)
    last_at = db.Column(db.DateTime)
    
    # Relationship Attribute
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
class Feedback(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    opinion = db.Column(db.String(100),nullable=False)
    send_at = db.Column(db.DateTime)
    
    # Relationship Attribute
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)