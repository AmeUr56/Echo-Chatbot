from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from wtforms import StringField,EmailField,PasswordField,SubmitField,HiddenField
from wtforms.validators import Length,DataRequired,EqualTo,Optional,ValidationError

import time

class SignupForm(FlaskForm):
    username = StringField(label='username',validators=[DataRequired(message="Username is required"),Length(min=5,max=10,message="Name Length must be between 5 and 10")])
    email = EmailField(label='email',validators=[DataRequired(message="Email is required")])
    password = PasswordField(label='password',validators=[DataRequired(message="Password required"),Length(8,30,message="Password Length must be between 8 and 30")])
    confirm_password = PasswordField(label='confirm_password',validators=[DataRequired(message="Confirm Password is required"),EqualTo('password',message='Passwords do not match')])
    honeypot = HiddenField(label='honeypot')
    timestamp = HiddenField(label='timestamp',default=time.time())

    submit = SubmitField(label='Enter')

    def validate_honeypot(self, field):
        if field.data:
            raise ValidationError("Spam detected!")
        
    def validate_timestamp(self, field):
        current_time = time.time()
        time_taken = current_time - float(field.data)
        if time_taken < 3:
            raise ValidationError("Form submitted too quickly! Possible bot activity.")

class LoginForm(FlaskForm):
    credentials = StringField(label='credentials',validators=[DataRequired(message="Email/Username is required")])
    password = PasswordField(label='password',validators=[DataRequired(message="Password is required")])
    honeypot = HiddenField(label='honeypot')
    timestamp = HiddenField(label='timestamp',default=time.time())
    
    submit = SubmitField(label='Enter')
    
    def validate_honeypot(self, field):
        if field.data:
            raise ValidationError("Spam detected!")
        
    def validate_timestamp(self, field):
        current_time = time.time()
        time_taken = current_time - float(field.data)
        if time_taken < 3:
            raise ValidationError("Form submitted too quickly! Possible bot activity.")
        
class LogoutForm(FlaskForm):
    pass

class FeedbackForm(FlaskForm):
    opinion = StringField(label='opinion',validators=[DataRequired(message="Opinion is required"),Length(min=10,max=300,message='Opinion Length must be between 10 and 300')])
    
    submit = SubmitField(label='submit')

class UpdateProfileForm(FlaskForm):
    name = StringField(label='name',validators=[Optional(),Length(min=5,max=10,message="Name Length must be between 5 and 10")])
    picture = FileField(label='profile_picture',validators=[Optional(),FileAllowed(['png','jpg','jpeg','gif'],message='Only PNG,JPG,JPEG,GIF supported')])
    new_password = PasswordField(label='new Password',validators=[Optional(),Length(8,30,message="New Password Length must be between 8 and 30")])
    password = PasswordField(label='password', validators=[DataRequired(message="Password is required")])
