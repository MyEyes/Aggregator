from flask_login import current_user, login_user, logout_user, login_url
from app.gui import bp
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask import render_template, redirect, url_for
from app.models.user import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

@bp.route('/login', methods=['GET', 'POST'])
def login():
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

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('gui.dashboard'))