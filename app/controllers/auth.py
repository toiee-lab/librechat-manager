from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError
from datetime import datetime

from app.models.user import SuperUser, Teacher, get_user_by_email
from app.models import db
from app.models.logs import SystemLog

auth_bp = Blueprint('auth', __name__)

class LoginForm(FlaskForm):
    email = StringField('メールアドレス', validators=[DataRequired(), Email()])
    password = PasswordField('パスワード', validators=[DataRequired()])
    submit = SubmitField('ログイン')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # すでにログインしている場合はリダイレクト
    if current_user.is_authenticated:
        if current_user.user_type == 'super_user':
            return redirect(url_for('super_user.dashboard'))
        else:
            return redirect(url_for('teacher.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = get_user_by_email(form.email.data)
        
        if user and user.check_password(form.password.data):
            login_user(user)
            
            # 最終ログイン時間を更新
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # ログを記録
            SystemLog.log_action(
                user_id=user.id,
                user_type=user.user_type,
                action='ログイン',
                ip_address=request.remote_addr
            )
            
            # ユーザータイプに基づいてリダイレクト
            if user.user_type == 'super_user':
                return redirect(url_for('super_user.dashboard'))
            else:
                return redirect(url_for('teacher.dashboard'))
        else:
            flash('メールアドレスまたはパスワードが無効です', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    # ログを記録
    SystemLog.log_action(
        user_id=current_user.id,
        user_type=current_user.user_type,
        action='ログアウト',
        ip_address=request.remote_addr
    )
    
    logout_user()
    flash('ログアウトしました', 'info')
    return redirect(url_for('auth.login'))