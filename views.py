from flask_admin import Admin,BaseView,expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.base import AdminIndexView
from flask_admin.actions import action
from flask_login import current_user
from flask import redirect,url_for,send_from_directory,send_file,request,flash,after_this_request,session
from sqlalchemy.sql import text,func

import os
from datetime import datetime,timezone,timedelta
from PIL import Image
import pathlib
import zipfile

from app import db,bcrypt
from forms import CreateRoleForm,EditRoleForm,CreateUserForm,EditUserForm,CreatePictureForm,FilterForm,DeleteForm,DateRangeForm
from models import User,Stats,Role
from plot import create_signup_dates_plot

class DashboardView(AdminIndexView):    
    @expose('/')
    def index(self):
        form = DateRangeForm()
        total_users = User.query.count()
        
        now = datetime.now(timezone.utc)
        start_day = datetime(now.year,now.month,now.day,tzinfo=timezone.utc)
        end_day = start_day + timedelta(days=1) - timedelta(seconds=1)
        
        active_users = Stats.query.filter(Stats.last_at >= start_day,Stats.last_at <= end_day).count()
        
        signup_dates = [user.created_at for user in User.query.all()]
        
        if 'start_date' in session and 'end_date' in session:
            start_date = session['start_date']
            end_date = session['end_date']
            create_signup_dates_plot(signup_dates, start_date, end_date)
            
            session.pop("start_date",None)
            session.pop("end_date",None)
        
        else:
            create_signup_dates_plot(signup_dates)
        
        
        query = text('''
            SELECT 
                COUNT(CASE WHEN is_super_admin = TRUE THEN 1 END) AS super_admin_count,
                COUNT(CASE WHEN is_admin = TRUE THEN 1 END) AS admin_count
            FROM Role;
        ''')
        role_counts = db.session.execute(query).first()
        
        return self.render('admin/dashboard_admin.html',total_users=total_users,active_users=active_users,role_counts=role_counts,form=form)
    
    @expose('/date_range',methods=['POST'])
    def date_range(self):
        form = DateRangeForm()
        if form.validate_on_submit():
            start_date = form.start_date.data
            end_date = form.end_date.data
            
            signup_dates = [user.created_at for user in User.query.all()]
            create_signup_dates_plot(signup_dates,start_date,end_date)
            
            session['start_date'] = start_date
            session['end_date'] = end_date
            
            return redirect(url_for("admin.index"))
        
        else:
            for field,errors in form.errors.items():
                for error in errors:
                    flash(error,"danger")
                    return redirect(url_for('admin.index'))
    
    def is_accessible(self):
        return current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('index'))
    
class UserModelView(ModelView):
    column_list = ['id','google_id','is_admin','name','picture','email','password','ip_address','created_at','updated_at']
    
    @expose('/')
    def index(self):
        form = FilterForm()

        users = self.model.query.all()
        return self.render('admin/users_admin.html',column_list=self.column_list,users=users,form=form)
    
    @expose('/create',methods=['GET','POST'])
    def create(self):
        form = CreateUserForm()

        if request.method == 'POST':
            if form.validate_on_submit():
                name = form.name.data.lower().strip()
                email = form.email.data.lower().strip()
                password = form.password.data
                picture = form.picture.data

                hashed_password = bcrypt.generate_password_hash(password)
                user = self.model(name=name,email=email,password=hashed_password,picture=picture,ip_address=request.remote_addr,created_at=datetime.now(timezone.utc))
                
                try:
                    db.session.add(user)
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    flash(f"{e}","danger")
                    return redirect(url_for('user.index'))
            
                flash("Succefuly Created User","success")
                return redirect(url_for('user.index'))
            else:
                for field,errors in form.errors.items():
                    for error in errors:
                        flash(error,"danger")
                        return redirect(url_for('user.create'))
                    
        return self.render("admin/create_user.html",form=form)

    @expose('/edit/<user_id>', methods=['GET', 'POST'])
    def edit(self, user_id):
        user = self.model.query.filter_by(id=user_id).first()

        form = EditUserForm(obj=user)
        if request.method == 'POST':
            if form.validate_on_submit():
                user_id = form.id.data
                name = form.name.data.lower().strip()
                email = form.email.data.lower().strip()
                picture = form.picture.data

                user.id = user_id
                user.name = name
                user.email = email
                user.picture = picture

                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    flash(f"{e}","danger")
                    return redirect(url_for('user.index'))
                
                flash("Succefuly Updated User","success")
                return redirect(url_for('user.index'))
            else:
                for field,errors in form.errors.items():
                    for error in errors:
                        flash(error,"danger")
                        return redirect(url_for('user.edit'))
                    
        return self.render("admin/edit_user.html",form=form,user=user)

    @expose('/delete/<user_id>', methods=['GET','POST'])
    def delete(self,user_id):
        form = DeleteForm()

        if request.method == 'POST':
            if form.validate_on_submit():
                user = self.model.query.filter_by(id=user_id).first()
                try:
                    db.session.delete(user)
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    flash(f"{e}","danger")
                    return redirect(url_for('user.index'))

                flash("Succefuly Deleted User","success")
                return redirect(url_for('user.index'))
            else:
                    for field,errors in form.errors.items():
                        for error in errors:
                            flash(error,"danger")
                            return redirect(url_for('user.index'))

        return self.render("admin/delete_user.html",form=form,user_id=user_id)
        
    @expose("/filter",methods=['POST'])
    def filter(self):
        form = FilterForm()
        if form.validate_on_submit():
            user_id = form.user_id.data
            
            user = self.model.query.filter_by(id=user_id).all()
            return self.render("admin/users_admin.html",column_list=self.column_list,users=user,form=form)
        else:
            for field,errors in form.errors.items():
                for error in errors:
                    flash(error,"danger")
                    return redirect(url_for('user.index'))
                
    def is_accessible(self):
        return current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin.index'))
    
class RoleModelView(ModelView):
    column_list = ['id','user_id','is_super_admin','is_admin']

    @expose('/')
    def index(self):
        form = FilterForm()
        roles = self.model.query.all()
        return self.render('admin/roles_admin.html',column_list=self.column_list,roles=roles,form=form)
    
    @expose('/create',methods=['GET','POST'])
    def create(self):
        form = CreateRoleForm()
        
        if request.method == 'POST':
            if form.validate_on_submit():
                user_id = form.user_id.data
                is_super_admin = form.is_super_admin.data
                is_admin = form.is_admin.data

                # Check if This user_id exist
                if not User.query.filter_by(id=user_id).first():
                    flash("User doesnt exist","danger")
                    return redirect(url_for("role.create"))

                role = self.model(is_super_admin=is_super_admin,is_admin=is_admin,user_id=user_id)
                
                try:
                    db.session.add(role)
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    flash(f"{e}","danger")
                    return redirect(url_for('role.index'))
                
                flash("Succefuly Created Role","success")
                return redirect(url_for('role.index'))
            else:
                for field,errors in form.errors.items():
                    for error in errors:
                        flash(error,"danger")
                        return redirect(url_for('role.create'))
                    
        return self.render("admin/create_role.html",form=form)

    @expose('/edit/<user_id>', methods=['GET', 'POST'])
    def edit(self, user_id):
        role = self.model.query.filter_by(user_id=user_id).first()

        form = EditRoleForm(obj=role)
        if request.method == 'POST':
            if form.validate_on_submit():
                is_super_admin = form.is_super_admin.data
                is_admin = form.is_admin.data

                role.is_super_admin = is_super_admin
                role.is_admin = is_admin
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    flash(f"{e}","danger")
                    return redirect(url_for('role.index'))
                
                flash("Succefuly Updated Role","success")
                return redirect(url_for('role.index'))
            else:
                for field,errors in form.errors.items():
                    for error in errors:
                        flash(error,"danger")
                        return redirect(url_for('pfps.edit'))
                    
        return self.render("admin/edit_role.html",form=form,role=role)

    @expose('/delete/<user_id>', methods=['GET','POST'])
    def delete(self,user_id):
        form = DeleteForm()

        if request.method == 'POST':
            if form.validate_on_submit():
                role = self.model.query.filter_by(user_id=user_id).first()
                    
                try:
                    db.session.delete(role)
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    flash(f"{e}","danger")
                    return redirect(url_for('role.index'))
                
                flash("Succefuly Deleted Role","success")
                return redirect(url_for('role.index'))
            else:
                for field,errors in form.errors.items():
                    for error in errors:
                        flash(error,"danger")
                        return redirect(url_for('role.index'))
                    
        return self.render("admin/delete_role.html",form=form,user_id=user_id)

    @expose("/filter",methods=['POST'])
    def filter(self):
        form = DeleteForm()
        filter_form = FilterForm()
        if filter_form.validate_on_submit():
            user_id = filter_form.user_id.data
            
            user_role = self.model.query.filter_by(user_id=user_id).all()
            return self.render("admin/roles_admin.html",column_list=self.column_list,roles=user_role,filter_form=filter_form,form=form)
        else:
            for field,errors in filter_form.errors.items():
                for error in errors:
                    flash(error,"danger")
                    return redirect(url_for('role.index'))
                
    def is_accessible(self):
        return current_user.is_super_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin.index'))

class StatsModelView(ModelView):        
    column_list = ['id','user_id','prompts','length','last_at']

    @expose("/")
    def index(self):
        form = FilterForm()
        stats = self.model.query.all()
        return self.render("admin/stats_admin.html",column_list=self.column_list,stats=stats,form=form)

    @expose("/filter",methods=['POST'])
    def filter(self):
        form = FilterForm()
        if form.validate_on_submit():
            user_id = form.user_id.data
            
            user_stats = self.model.query.filter_by(user_id=user_id).all()
            return self.render("admin/stats_admin.html",column_list=self.column_list,stats=user_stats,form=form)
        else:
            for field,errors in form.errors.items():
                for error in errors:
                    flash(error,"danger")
                    return redirect(url_for('stats.index'))
                
    def is_accessible(self):
        return current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin.index'))
    
class FeedbackModelView(ModelView):
    column_list = ['id','user_id','opinion','send_at']

    @expose("/")
    def index(self):
        form = FilterForm()
        feedbacks = self.model.query.all()
        return self.render("admin/feedbacks_admin.html",column_list=self.column_list,feedbacks=feedbacks,form=form)

    @expose("/filter",methods=['POST'])
    def filter(self):
        form = FilterForm()
        if form.validate_on_submit():
            user_id = form.user_id.data
            
            user_feedbacks = self.model.query.filter_by(user_id=user_id).all()
            return self.render("admin/feedbacks_admin.html",column_list=self.column_list,feedbacks=user_feedbacks,form=form)
        else:
            for field,errors in form.errors.items():
                for error in errors:
                    flash(error,"danger")
                    return redirect(url_for('feedback.index'))
                
    def is_accessible(self):
        return current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin.index'))
    
class DiscussionModelView(ModelView):
    column_list = ['id','user_id','index','prompt','response']

    @expose("/")
    def index(self):
        form = FilterForm()
        discussions = self.model.query.all()
        return self.render("admin/discussions_admin.html",column_list=self.column_list,discussions=discussions,form=form)
    
    @expose("/filter",methods=['POST'])
    def filter(self):
        form = FilterForm()
        if form.validate_on_submit():
            user_id = form.user_id.data
            
            user_discussion = self.model.query.filter_by(user_id=user_id).all()
            return self.render("admin/discussions_admin.html",column_list=self.column_list,discussions=user_discussion,form=form)
        else:
            for field,errors in form.errors.items():
                for error in errors:
                    flash(error,"danger")
                    return redirect(url_for('discussion.index'))
                
    def is_accessible(self):
        return current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin.index'))
    
class ProfilePicturesView(BaseView):
    dir_path = 'static/pfps'

    @expose('/')
    def index(self):
        user_ids = os.listdir(self.dir_path)
        user_ids = [user_id for user_id in user_ids if user_id.endswith("png")]
        return self.render('admin/pfps_admin.html',user_ids=user_ids)
    
    @expose('/create',methods=['GET','POST'])
    def create(self):
        form = CreatePictureForm()

        if request.method == 'POST':
            if form.validate_on_submit():
                user_id = form.user_id.data
                picture = form.picture.data

                # Check if This user_id exist
                user = User.query.filter_by(id=user_id).first()
                if not user:
                    flash("User doesnt exist","danger")
                    return redirect(url_for("pfps.create"))
                
                # Check if This user_id already has Profile Picture
                if f"{user_id}.png" in os.listdir(self.dir_path):
                    flash("User already has Profile Picture","danger")
                    return redirect(url_for("pfps.create"))

                picture_pil = Image.open(picture.stream)
                picture_pil = picture_pil.resize((180,180))

                # Save Picture
                file_path = rf"{self.dir_path}/{user_id}.png"
                picture_pil.save(file_path,"PNG")
                
                user.picture = True

                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    flash(f"{e}","danger")
                    return redirect(url_for("pfps.index"))

                flash("Succefuly Uploaded Picture",'success')
                return redirect(url_for("pfps.index"))
            else:
                for field,errors in form.errors.items():
                    for error in errors:
                        flash(error,"danger")
                        return redirect(url_for('pfps.create'))
                    
        return self.render("admin/create_pfps.html",form=form)
    
    @expose('/preview/<user_id>')
    def preview(self,user_id):
        dir_path = 'static/pfps'
        return send_from_directory(dir_path,user_id)
    
    @expose('/delete/<user_id>',methods=['GET','POST'])
    def delete(self,user_id):
        form = DeleteForm()
        
        if request.method == 'POST':
            if form.validate_on_submit():
                dir_path = 'static/pfps'
                os.remove(fr"{dir_path}/{user_id}")
                user = User.query.filter_by(id=user_id.split('.')[0]).first()
                user.picture = False

                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    flash(f"{e}","danger")
                    return redirect(url_for('pfps.index'))
                
                flash("Succefuly Deleted Profile Picture","success")
                return redirect(url_for('pfps.index'))
            
        return self.render("admin/delete_pfps.html",form=form,user_id=user_id)
    
    def is_accessible(self):
        return current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('/admin'))
    
class FeaturesView(BaseView):
    @expose('/')
    def index(self):
        if os.path.exists("profile_pictures.zip"):
            os.remove("profile_pictures.zip")
        
        return self.render('admin/features_admin.html')

    @expose('/install_db')
    def install_db(self):
        return send_file("instance/echo_bot.db",as_attachment=True)
    
    @expose('/install_pfps')
    def install_pfps(self):
        dir = pathlib.Path("static/pfps")
        
        with zipfile.ZipFile("profile_pictures.zip","w") as archive:
            for file_path in dir.iterdir():
                archive.write(file_path,arcname=file_path.name)
                
        return send_file("profile_pictures.zip")

    def is_accessible(self):
        return current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('/admin'))
    
