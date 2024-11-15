from flask import render_template,redirect,request,url_for,flash,jsonify
from flask_login import login_user,logout_user,login_required,current_user
from flask_admin import AdminIndexView

from datetime import datetime,timezone
from PIL import Image
import re
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException
import time

from forms import SignupForm,LoginForm,LogoutForm,FeedbackForm,UpdateProfileForm
from models import User,Feedback,Role

def register_routes(app,db,bcrypt,limiter,cache):

    @app.route('/')
    @limiter.limit("5 per second")
    def index():
        user_data = {
            'picture_path': current_user.id if current_user.picture else False,
            'is_super_admin': current_user.is_super_admin,
            'is_admin': current_user.is_admin
        }
        forms = {
            'feedback_form': FeedbackForm(),
            'logout_form': LogoutForm()
        }
        return render_template('HomePage.html',forms=forms,user_data=user_data)
    
    @app.route('/signup',methods=['GET','POST'])
    @limiter.limit("10 per minute")
    def signup():
        form = SignupForm()

        if request.method == 'POST':
            if form.validate_on_submit():
                username = form.username.data.lower().strip()
                email = form.email.data.lower().strip()
                password = form.password.data
                confirm_password = form.confirm_password.data


                # Check if email already exists 
                if User.query.filter_by(email=email).first():
                    return jsonify({"status":"error","message":"Email already exists"})
            
                # Check if username is already taken
                if User.query.filter_by(name=username).first():
                    return jsonify({"status":"error","message":"Username already taken"})
                
                # Hash the password
                hashed_password = bcrypt.generate_password_hash(password)
                
                # Create user object
                new_user = User(name=username,email=email,password=hashed_password,ip_address=request.remote_addr,created_at=datetime.now(timezone.utc))

                # Add user to the db
                db.session.add(new_user)
                db.session.commit()

                # Add role to the db
                user_role = Role(user_id=new_user.id)
                db.session.add(user_role)
                db.session.commit()

                flash("Registrated Succefully","success")
                return jsonify({"status": "redirect", "url": url_for('login')})

            else:
                # Display Errors if form validation fails
                for field, errors in form.errors.items():
                    for error in errors:
                        if error == "The response parameter is missing.":
                            error = "reCAPTCHA not solved"
                        return jsonify({"status":"error","message":f'{error}'})
        
        current_time = time.time() 
        return render_template('Signup.html',form=form,form_endpoint='signup',current_time=current_time)
    
    def is_email(email):
        # Regular expression for validating an Email
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        
        # Return True if the email matches the regex
        if re.match(email_regex, email):
            return True
        else:
            return False
        
    @app.route('/login',methods=['GET','POST'])
    @limiter.limit("5 per minute")
    def login():
        if current_user.is_authenticated:
            flash("Already Logged in","error")
            return redirect(url_for('index'))
        
        form = LoginForm()

        if request.method == 'POST':
            if form.validate_on_submit():
                credentials = form.credentials.data.lower().strip()
                password = form.password.data
                
                if is_email(credentials):
                    user = User.query.filter_by(email=credentials).first()
                else:
                    user = User.query.filter_by(name=credentials).first()
                    
                # Check if User exists
                if user:
                    # Check if Password is correct
                    if bcrypt.check_password_hash(user.password,password):
                        login_user(user)
                        flash("Logged in Succefully","success")
                        return jsonify({"status": "redirect", "url": url_for('index')})
            
                    else:
                        return jsonify({"status":"error","message":"Password incorrect"})
                else:
                    return jsonify({"status":"error","message":"Email or Username do not exist"})
                        
            else:
                for field,errors in form.errors.items():
                    for error in errors:
                        if error == "The response parameter is missing.":
                            error = "reCAPTCHA not solved"
                        return jsonify({"status":"error","message":f'{error}'})
        
        current_time = time.time() 
        return render_template('Login.html',form=form,form_endpoint='login',current_time=current_time)

    @app.route('/logout',methods=['POST'])
    @limiter.limit("3 per second")
    def logout():
        form = LogoutForm()
        if form.validate_on_submit() and current_user.is_authenticated:
            logout_user() 
            flash("Logged out Succefully","success")
            return redirect(url_for('index'))
        else:
            flash("Login Required","error")
            return redirect(url_for('login'))
    
    @app.route('/feedback',methods=['POST'])
    @limiter.limit("3 per second")
    def feedback():
        form = FeedbackForm()
        if form.validate_on_submit() and current_user.is_authenticated:
            opinion = form.opinion.data
            feedback = Feedback(opinion=opinion,user_id=current_user.id,send_at=datetime.now(timezone.utc))
                        
            db.session.add(feedback)
            db.session.commit()

            flash("Thank you for the feedback")
            return redirect(url_for('index'))
        else:
            flash("Login Required","error")
            return redirect(url_for('login'))

    @app.route('/profile',methods=['GET','POST'])
    @limiter.limit("5 per second")
    @login_required
    @cache.cached(timeout=300,key_prefix=lambda:f"user_{current_user.id}")
    def profile():
        form = UpdateProfileForm()

        user = User.query.filter_by(id=current_user.id).first()
        if request.method == 'POST':
            if form.validate_on_submit():
                name = form.name.data.strip()
                new_password = form.new_password.data
                password = form.password.data
                picture =  form.picture.data

                if not bcrypt.check_password_hash(user.password,password):
                    return jsonify({"status":"error","message":"Password incorrect"})
                
                is_updated = 0
                if name:
                    user.name = name
                    is_updated = 1

                if new_password:
                    user.password = bcrypt.generate_password_hash(new_password)
                    is_updated = 1

                if picture:
                    picture_pil = Image.open(picture.stream)
                    picture_pil = picture_pil.resize((180,180))
                    
                    # Save Picture
                    file_path = rf"static/pfps/{current_user.id}.png"
                    picture_pil.save(file_path,"PNG")
                    
                    user.picture = True
                    is_updated = 1

                if is_updated:
                    user.updated_at = datetime.now(timezone.utc)

                # Commit Changes to the db
                db.session.commit()

                flash("Updated Profile Succefully")
                return jsonify({"status":"redirect","url":url_for("profile")})

            else:
                for field,errors in form.errors.items():
                    for error in errors:
                        if error == "The response parameter is missing.":
                            error = "reCAPTCHA not solved"
                        return jsonify({"status":"error","message":error})
                    
        user_data = {
            'username':user.name,
            'picture_path': current_user.id if current_user.picture else False,
            'is_super_admin': current_user.is_super_admin,
            'is_admin': current_user.is_admin
        }
        return render_template('profile.html',form=form,user_data=user_data)
    
    @app.errorhandler(HTTPException)
    def handle_error(error):
        if error.code == 403 or error.code == 404:
            return render_template('Error.html')
    
    @app.template_filter("underscore_separate")
    def underscore_separate(s):
        s = s.split("_")
        s = " ".join(s)
        return s