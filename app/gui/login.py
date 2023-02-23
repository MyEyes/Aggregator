from flask_login import current_user, login_user, logout_user, login_url
from app.gui import bp
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask import render_template, redirect, url_for
from app.models.user import User
from app.models import db

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class CreateAdminForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_confirm = PasswordField('Password Confirm', validators=[DataRequired()])
    create = SubmitField('Create Admin Account')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    #If no user account exists allow creation of admin account
    if not User.query.first():
        return admin_account()
    #If logged in go to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('gui.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            return redirect(url_for('gui.login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('gui.dashboard'))
    return render_template('login.html', title='Sign In', form=form)

def admin_account():
    form = CreateAdminForm()
    if form.validate_on_submit():
        if form.password.data == form.password_confirm.data:    
            user = User()
            user.name = form.username.data
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('gui.login'))
    return render_template('create_admin.html', title='Create Admin', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('gui.dashboard'))