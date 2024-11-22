from flask import render_template,request,redirect,request,url_for,flash,jsonify,session
from flask_login import login_user,logout_user,login_required,current_user
from flask_admin import AdminIndexView
from sqlalchemy.sql import text

from datetime import datetime,timezone
from PIL import Image
import re
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException
import time
import requests
from io import BytesIO

from forms import SignupForm,LoginForm,LogoutForm,FeedbackForm,UpdateProfileForm,ClearDiscussion
from models import User,Feedback,Role,Discussion,Stats
from chat import echo_response,activate_echo#,query
from script import create_conversation_history

def register_routes(app,db,bcrypt,limiter,cache,socketio,google):
    
    #-----------------------------------------Restful API----------------------------------------#
    @app.route('/')
    @limiter.limit("5 per second")
    def index():
        session.permanent = True
        
        query = text("""
            SELECT u.id,u.name,u.picture,s.length,s.prompts
            FROM Stats as s
            INNER JOIN User as u
                ON s.user_id = u.id
            ORDER BY s.length DESC,s.prompts DESC
            LIMIT 2;
        """)
        
        ranking = db.session.execute(query).all()
        
        user_data = {
            'picture_path': current_user.id if current_user.picture else False,
            'is_super_admin': current_user.is_super_admin,
            'is_admin': current_user.is_admin,
        }
        forms = {
            'feedback_form': FeedbackForm(),
            'logout_form': LogoutForm(),
            'clear_discussion':ClearDiscussion()
        }
    
        return render_template('HomePage.html',forms=forms,user_data=user_data,ranking=ranking)
    
    @app.route('/signup',methods=['GET','POST'])
    @limiter.limit("1 per second")
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

                flash("Registrated Succefully","success")
                return jsonify({"status": "redirect", "url": url_for('login')})

            else:
                for field,errors in form.errors.items():
                    for error in errors:
                        return jsonify({"status":"error","message":error})
        
        current_time = time.time() 
        return render_template('Signup.html',form=form,form_endpoint='signup',current_time=current_time)
    
    @app.route('/login',methods=['GET','POST'])
    @limiter.limit("5 per second")
    def login():
        if current_user.is_authenticated:
            flash("Already Logged in","error")
            return redirect(url_for('index'))
        
        form = LoginForm()

        if request.method == 'POST':
            if form.validate_on_submit():
                credentials = form.credentials.data.lower().strip()
                password = form.password.data
                
                user_name = User.query.filter_by(name=credentials).first()
                user_email = User.query.filter_by(email=credentials).first()
                if user_email:
                    if user_email.google_id:
                        return jsonify({"status":"error","message":"Login with Google Account"})
                    user = user_email
                
                if user_name:
                    if user_name.google_id:
                        return jsonify({"status":"error","message":"Login with Google Account"})
                    user = user_name
                
                # Check if User exists
                if user:
                    # Check if Password is correct
                    if bcrypt.check_password_hash(user.password,password):
                        login_user(user)
                        flash("Logged in Succefully","success")
                        return jsonify({"status":"redirect","url": f"{url_for('index')}"})
                    else:
                        return jsonify({"status":"error","message":"Password incorrect"})
                else:
                    return jsonify({"status":"error","message":"Email or Username do not exist"})
    
            else:
                for field,errors in form.errors.items():
                    for error in errors:
                        return jsonify({"status":"error","message":error})
        
        current_time = time.time() 
        return render_template('Login.html',form=form,form_endpoint='login',current_time=current_time)

    @app.route('/login/google')
    def login_google():
        if current_user.is_authenticated:
            flash("Already Logged in","error")
            return redirect(url_for('index'))
        
        redirect_uri = url_for("authorize_google",_external=True)
        return google.authorize_redirect(redirect_uri)
    
    @app.route("/authorize/google")
    def authorize_google():
        if current_user.is_authenticated:
            flash("Already Logged in","error")
            return redirect(url_for('index'))
        
        token = google.authorize_access_token()
        userinfo_endpoint = google.server_metadata['userinfo_endpoint']
        response = google.get(userinfo_endpoint)
        user_info = response.json()
        
        google_id = user_info['sub']
        user =  User.query.filter_by(google_id=google_id).first()
        if user:
            login_user(user)
            flash("Logged in Succefully","success")
            return redirect(url_for("index"))
        
        username = user_info['name'].lower().strip()
        email = user_info['email'].lower().strip()
        
        user = User(google_id=google_id,name=username,email=email,ip_address=request.remote_addr,created_at=datetime.now(timezone.utc))
        db.session.add(user)
        db.session.commit()
        
        profile_pic_url = user_info['picture']
        if profile_pic_url:
            response = requests.get(profile_pic_url)
            if response.status_code == 200:
                    image_stream = BytesIO(response.content)
                    picture_pil = Image.open(image_stream)
                    picture_pil = picture_pil.resize((180,180))
                    
                    # Save Picture
                    file_path = rf"static/pfps/{user.id}.png"
                    picture_pil.save(file_path,"PNG")
                    user.picture = True
        
        db.session.commit()
        
        login_user(user)
        flash("Logged in Succefully","success")
        return redirect(url_for("index"))
        
    @app.route('/logout',methods=['POST'])
    @limiter.limit("3 per second")
    def logout():
        form = LogoutForm()
        if form.validate_on_submit() and current_user.is_authenticated:
            logout_user() 
            session.clear()
            flash("Logged out Succefully","success")
            return redirect(url_for('index'))
        else:
            flash("Login Required","error")
            return redirect(url_for('login'))

    @app.route('/feedback',methods=['POST'])
    @limiter.limit("1 per second")
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
    
    @cache.cached(timeout=30,key_prefix=lambda:f"user_{current_user.id}")
    def get_userdata():
        user = User.query.filter_by(id=current_user.id).first()

        
        query = text("""
            SELECT prompts,length
            FROM Stats
            WHERE user_id = :user_id
        """)
        stats = db.session.execute(query,{"user_id":user.id}).first()
        
        user_data = {
            'username':user.name,
            'picture_path': current_user.id if current_user.picture else False,
            'is_super_admin': current_user.is_super_admin,
            'is_admin': current_user.is_admin,
            'is_oauth':current_user.google_id,
            'stats':stats
        }
        return user_data
    
    @app.route('/profile',methods=['GET','POST'])
    @limiter.limit("5 per second")
    @login_required
    def profile():
        user = User.query.filter_by(id=current_user.id).first()
        
        oauth = True if current_user.google_id else False 
        form = UpdateProfileForm(oauth_user=oauth)
        if request.method == 'POST':
            if form.validate_on_submit():
                name = form.name.data.strip()
                picture =  form.picture.data    
            
                if not current_user.google_id:
                    new_password = form.new_password.data
                    password = form.password.data

                    if not bcrypt.check_password_hash(user.password,password):
                        return jsonify({"status":"error","message":"Password incorrect"})

                    if new_password:
                        user.password = bcrypt.generate_password_hash(new_password)
                        is_updated = 1
                
                is_updated = 0
                if name:
                    user.name = name
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
                        return jsonify({"status":"error","message":error})
                    
        user_data = get_userdata()
        return render_template('profile.html',form=form,user_data=user_data)
   
    @app.route('/clear_discussion',methods=['POST'])
    @limiter.limit("1 per second")
    @login_required
    def clear_discussion():
        form = ClearDiscussion()
        if form.validate_on_submit():
            discussions = Discussion.query.filter_by(user_id=current_user.id).all()

            if not discussions:
                flash("No discussions to clear",'error')
                return redirect(url_for('index'))
        
            for discussion in discussions:
                db.session.delete(discussion)
            db.session.commit()
        
            flash("Discussion Succefuly Cleared",'success')
            return redirect(url_for('index'))
    #--------------------------------------------------------------------------------------#
    #---------------------------------------SocketIO API-----------------------------------#
    user_conversations = {}
    @socketio.on('connect')
    @login_required
    def handle_connect():
        user_id = current_user.id

        # Fetch the length of discussion
        latest_stats = Stats.query.filter_by(user_id=user_id).first()
        if not latest_stats:
            stats = Stats(user_id=user_id,last_at=datetime.now(timezone.utc),prompts=0)
            db.session.add(stats)
            db.session.commit()
            session['discussion_length'] = 0
        else:
            session['discussion_length'] = latest_stats.length

        del latest_stats

        # Fetch the latest discussion index
        latest_discussion = Discussion.query.filter_by(user_id=user_id).order_by(Discussion.index.desc()).first()
        session['discussion_index'] = latest_discussion.index if latest_discussion else 0

        del latest_discussion
        if not session['discussion_index']:
            user_conversations[user_id] = []

        # Fetch the Number of Prompts from Stats
        num_prompts = Stats.query.filter_by(user_id=user_id).first().prompts
        session['prompts'] = num_prompts
        
        del num_prompts
        
        # Fetch the Prompts & Responses for user
        query = text("""
            SELECT prompt,response
            FROM Discussion
            WHERE user_id = :user_id
            ORDER BY "index"
        """)

        result = db.session.execute(query, {'user_id': current_user.id})

        user_conversations[user_id] = create_conversation_history(result)

        user_conversation = user_conversations[user_id]
        formatted_conversation = []
        for i in range(0,session['discussion_index']*2,2):
            prompt = user_conversation[i]['content']
            response = user_conversation[i+1]['content']
            formatted_conversation.append({
                "user_message": prompt,
                "ai_response": response
            })
        del user_conversation
        
        socketio.emit("conversation_history", formatted_conversation, to=request.sid)
        activate_echo()
        
    @socketio.on('send_message')
    @login_required
    def handle_message(message):            
        user_id = current_user.id

        # Get conversation history
        history = user_conversations[user_id]

        sid = request.sid
        response = []
        for word in echo_response(history,message):
            socketio.emit("receive_message", word,to=sid)
            response.append(word)
         
        session['discussion_index'] += 1
        
        response = "".join(response)

        new_discussion = Discussion(prompt=message,response=response,index=session['discussion_index'],user_id=current_user.id)
        db.session.add(new_discussion)
        db.session.commit()
        
        session['discussion_length'] += len(message)
        session['prompts'] += 1
    
    #@socketio.on('send_audio')
    #@login_required
    #def handle_audio_data(data):
    #    sid = request.sid
    #
    #   filename = fr"static/audio/{current_user.id}.wav"
    #    with open(filename, 'wb') as f:
    #        f.write(data)
    #    
    #    transcription = query(filename).get("text","")
    #    socketio.emit("receive_message",transcription,to=sid)
    

    @socketio.on("disconnect")
    def handle_user_disconnect():
        user_id = current_user.id

        stats = Stats.query.filter_by(user_id=user_id).first()
        stats.length = session['discussion_length']
        stats.last_at = datetime.now(timezone.utc)
        stats.prompts = session['prompts']
        
        db.session.commit()

        if user_id in user_conversations.keys():
            del user_conversations[user_id]
        
        for elem in ['discussion_index','discussion_length','last_at']:
            session.pop(elem,None)
    #--------------------------------------------------------------------------------------#
    
    #------------------------------------------Addons--------------------------------------#
    @app.errorhandler(HTTPException)
    def handle_error(error):
        return render_template('Error.html')
    

    @app.template_filter("underscore_separate")
    def underscore_separate(s):
        s = s.split("_")
        s = " ".join(s)
        return s
    
    @app.template_filter("get_attr")
    def get_attr(entity,attr):
        return getattr(entity,attr,None)
    #--------------------------------------------------------------------------------------#
    