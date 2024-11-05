from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from flask_wtf.recaptcha import RecaptchaField
from wtforms import StringField,EmailField,PasswordField,SubmitField
from wtforms.validators import Length,DataRequired,EqualTo

class SignupForm(FlaskForm):
    username = StringField(label='username',validators=[DataRequired(),Length(min=5,max=10,message="Name Length between 5 and 10")])
    email = EmailField(label='email',validators=[DataRequired()])
    password = PasswordField(label='password',validators=[DataRequired(),Length(8,30,message="Password Length between 8 and 30")])
    confirm_password = PasswordField(label='confirm_password',validators=[DataRequired(),EqualTo('password',message='Passwords are different')])
    recaptcha = RecaptchaField()
    
    submit = SubmitField(label='submit')

class LoginForm(FlaskForm):
    email = EmailField(label='email',validators=[DataRequired()])
    password = PasswordField(label='password',validators=[DataRequired()])
    recaptcha = RecaptchaField()
    
    submit = SubmitField(label='submit')

class LogoutForm(FlaskForm):
    submit = SubmitField(label='submit')

class FeedbackForm(FlaskForm):
    opinion = StringField(label='opinion',validators=[DataRequired(),Length(min=10,max=100,message='Opinion Length between 10 and 100')])
    
    submit = SubmitField(label='submit')

class ModifyPictureForm(FlaskForm):
    picture = FileField('profile_picture',validators=[DataRequired(),FileAllowed(['png','jpg','jpeg','gif'],'Only PNG,JPG,JPEG,GIF supported')])
    password = PasswordField(label='password',validators=[DataRequired()])
    
    submit = SubmitField(label='submit')
    
class ModifyUsernameForm(FlaskForm):
    username = StringField(label='username',validators=[DataRequired(),Length(min=5,max=10,message="Name Length between 5 and 10")])
    password = PasswordField(label='password',validators=[DataRequired()])

    submit = SubmitField(label='submit')

class ModifyPasswordForm(FlaskForm):
    password = PasswordField(label='password',validators=[DataRequired()])
    new_password = PasswordField(label='password',validators=[DataRequired(),Length(8,30,message="Password Length between 8 and 30")])

    submit = SubmitField(label='submit')
