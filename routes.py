from flask import render_template,redirect,request,url_for,flash
from flask_login import login_user,logout_user,login_required,current_user
from flask_admin import AdminIndexView

from flask_limiter.util import get_remote_address

from datetime import datetime

from forms import SignupForm,LoginForm,LogoutForm,FeedbackForm
from models import User,Feedback

# Admin Panel
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return 1#current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('index'))

def register_routes(app,db,bcrypt,limiter):
    @app.route('/')
    def index():
        form = FeedbackForm()
        return render_template('HomePage.html',form=form,ip=get_remote_address())
    
    @limiter.limit("3 per second")
    @app.route('/signup',methods=['GET','POST'])
    def signup():
        if request.method == 'POST':
            form = SignupForm()
            if form.validate_on_submit():
                username = form.username.data.lower()
                email = form.email.data.lower()
                password = form.password.data
                confirm_password = form.confirm_password.data

                # Check if username is already taken
                if User.query.filter_by(name=username):
                    pass 
                # Check if email is already taken
                elif User.query.filter_by(email=email):
                    pass
                
                # Check if passwords are same
                elif not (password == confirm_password):
                    pass
            
                # Hash the password
                hashed_password = bcrypt.generate_password_hash(password)
                
                # Create user object
                new_user = User(name=username,email=email,password=hashed_password,created_at=datetime.utcnow())
                
                # Add it to the db
                db.session.add(new_user)
                db.session.commit()

                flash("-Registration Done-")

                return redirect(url_for('login'))
            
        return render_template('Signup.html')#,form=form)
        
    @app.route('/login',methods=['GET','POST'])
    def login():        
        if request.method == 'POST':
            form = LoginForm()
            if form.validate_on_submit():
                email = form.email.data.lower()
                password = form.password.data
                
                user = User.query.filter_by(email=email).first()
                # Check if User exists
                if user:
                    # Check if Password is correct
                    if bcrypt.check_password_hash(user.password) == password:
                        login_user(user)
                        flash("-Welcome-")
                        return redirect(url_for('index'))
                    
                    else:
                        pass
                else:
                    pass            

        return render_template('Login.html')#,form=form)
    
    @app.route('/logout',methods=['POST'])
    def logout():
        form = LogoutForm()
        if form.validate_on_submit() and current_user.is_authenticated:
            logout_user() 
            flash("-Logout Succefully-")
            return redirect(url_for('index'))
        else:
            flash('Login Required')
            return redirect(url_for('login'))
        
    @limiter.limit("1 per second")
    @app.route('/feedback',methods=['POST'])
    def feedback():
        form = FeedbackForm()
        if form.validate_on_submit() and current_user.is_authenticated:
            opinion = form.opinion.data
            feedback = Feedback(opinion=opinion)
            
            db.session.add(feedback,user_id=current_user.id,send_at=datetime.utcnow())
            db.session.commit()
            flash("-Thank you for your feedback-")

            return redirect(url_for('index'))
        else:
            flash('Login Required')
            return redirect(url_for('login'))
        
    #@login_required
    @app.route('/profile')
    def profile():
        return render_template('profile.html')