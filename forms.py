from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from wtforms import StringField,EmailField,PasswordField,SubmitField,HiddenField,BooleanField,IntegerField,DateField
from wtforms.validators import Length,DataRequired,EqualTo,Optional,ValidationError,Regexp

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
            raise ValidationError("Spam detected")
        
    def validate_timestamp(self, field):
        current_time = time.time()
        time_taken = current_time - float(field.data)
        if time_taken < 3:
            raise ValidationError("Form submitted too fast!")
        
class LogoutForm(FlaskForm):
    pass

class FeedbackForm(FlaskForm):
    opinion = StringField(label='opinion',validators=[DataRequired(message="Opinion is required"),Length(min=10,max=300,message='Opinion Length must be between 10 and 300')])
    
    submit = SubmitField(label='submit')

class UpdateProfileForm(FlaskForm):
    name = StringField(label='name',validators=[Optional(),Length(min=5,max=10,message="Name Length must be between 5 and 10")])
    picture = FileField(label='profile_picture',validators=[Optional(),FileAllowed(['png','jpg','jpeg','gif'],message='Only PNG,JPG,JPEG,GIF supported')])
    new_password = PasswordField(label='new Password',validators=[Optional(),Length(8,30,message="New Password Length must be between 8 and 30")])
    password = PasswordField(label='password', validators=[])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.oauth_user = kwargs.get('oauth_user', False)

    def validate_password(self, field):
        if self.oauth_user:
            return 
        if not field.data:
            raise ValidationError("Password is required")
        
class ClearDiscussion(FlaskForm):
    pass


# Admin Forms
#----------------User----------------#
class CreateUserForm(FlaskForm):
    name = StringField(label='name',validators=[DataRequired(message="Username is required"),Length(min=5,max=10,message="Name Length must be between 5 and 10")])
    email = EmailField(label='email',validators=[DataRequired(message="Email is required")])
    password = PasswordField(label='password',validators=[DataRequired(message="Password required"),Length(8,30,message="Password Length must be between 8 and 30")])
    picture = BooleanField(label="profile_picture",validators=[Optional()])

    submit = SubmitField(label="Create")

class EditUserForm(FlaskForm):
    id = IntegerField(label="id")
    name = StringField(label='username',validators=[Optional(),Length(min=5,max=10,message="Name Length must be between 5 and 10")])
    email = EmailField(label='email',validators=[Optional()])
    picture = BooleanField(label="profile_picture",validators=[Optional()])

    submit = SubmitField(label="Save Changes")

    def validate_id(self,field):
        if field.data > 9223372036854775807:
            raise ValidationError("Too Large Number")
        elif field.data < 0:
            raise ValidationError("Id cant be negative ")
        
#------------------------------------#

#----------------Role----------------#
class CreateRoleForm(FlaskForm):
    user_id = IntegerField(label="user_id")
    is_super_admin = BooleanField(label="is_super_admin",validators=[Optional()])
    is_admin = BooleanField(label="is_admin",validators=[Optional()])
    
    submit = SubmitField(label="Create")

    def validate_user_id(self,field):
        if field.data > 9223372036854775807:
            raise ValidationError("Too Large Number")
        elif field.data < 0:
            raise ValidationError("Id cant be negative ")
        
class EditRoleForm(FlaskForm):
    is_super_admin = BooleanField(label="is_super_admin",validators=[Optional()])
    is_admin = BooleanField(label="is_admin",validators=[Optional()])
        
    submit = SubmitField(label="Save Changes")

#------------------------------------#

#----------------Pfps----------------#
class CreatePictureForm(FlaskForm):
    user_id = IntegerField(label="user_id")
    picture = FileField(label='profile_picture',validators=[DataRequired(message='Picture is required'),FileAllowed(['png','jpg','jpeg','gif'],message='Only PNG,JPG,JPEG,GIF supported')])
    
    submit = SubmitField(label="Create")

    def validate_user_id(self,field):
        if field.data > 9223372036854775807:
            raise ValidationError("Too Large Number")
        elif field.data < 0:
            raise ValidationError("Id cant be negative ")
#-------------------------------------#

#----------------Filter--------------#
class FilterForm(FlaskForm):
    user_id = IntegerField(label="user_id",validators=[DataRequired(message="Id is required")])

    submit = SubmitField(label="Filter")

    def validate_user_id(self,field):
        if field.data > 9223372036854775807:
            raise ValidationError("Too Large Number")
        elif field.data < 0:
            raise ValidationError("Id cant be negative ")

#------------------------------------#

#----------------Delete--------------#
class DeleteForm(FlaskForm):
    submit = SubmitField(label="Delete")
#------------------------------------#

#----------------DateRange--------------#
class DateRangeForm(FlaskForm):
    start_date = DateField("Start Date", format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField("End Date", format='%Y-%m-%d', validators=[DataRequired()])
    
    submit = SubmitField("Submit")

    def validate_end_date(self, end_date):
        if self.start_date.data and end_date.data and end_date.data < self.start_date.data:
            raise ValidationError("End date must be after the start date.")
#---------------------------------------#