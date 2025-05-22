from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError
from datetime import datetime

from app.models.user import SuperUser, Teacher, get_user_by_email, UserType
from app.models import db
from app.models.logs import SystemLog

auth_bp = Blueprint('auth', __name__)

class LoginForm(FlaskForm):
    email = StringField('メールアドレス', validators=[DataRequired(), Email()])
    password = PasswordField('パスワード', validators=[DataRequired()])
    submit = SubmitField('ログイン')

@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    # すでにログインしている場合はリダイレクト
    if current_user.is_authenticated:
        if current_user.user_type == UserType.SUPER_USER:
            return redirect(url_for('super_user.dashboard'))
        else:
            flash('管理者権限が必要です', 'danger')
            logout_user()
            return redirect(url_for('auth.admin_login'))
    
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        
        print(f"DEBUG - 管理者ログイン試行: {email}")
        
        # 講師が同じメールアドレスで存在するか確認
        teacher = Teacher.query.filter_by(email=email).first()
        if teacher:
            print(f"DEBUG - 同じメールアドレスの講師が存在します: {email}")
            flash('このメールアドレスは講師アカウントとして登録されています。講師ログインページからログインしてください。', 'warning')
            return redirect(url_for('auth.login'))
        
        # スーパーユーザーのみ検索
        user = SuperUser.query.filter_by(email=email).first()
        print(f"DEBUG - 管理者検索結果: {user}")
        
        if user and user.check_password(password):
            print(f"DEBUG - 管理者ログイン成功: {user.username}, ID: {user.id}")
            
            # ここで明示的にクラスをチェック
            if not isinstance(user, SuperUser):
                print(f"DEBUG - 深刻な型エラー: {type(user)}")
                flash('アカウントタイプのエラーが発生しました', 'danger')
                return redirect(url_for('auth.admin_login'))
            
            # カスタムIDを作成して保存
            user._id_with_prefix = f"S_{user.id}"
            print(f"DEBUG - カスタムID設定: {user._id_with_prefix}")
            
            login_user(user)
            
            # 最終ログイン時間を更新
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # ログを記録
            SystemLog.log_action(
                user_id=user.id,
                user_type=user.user_type,
                action='管理者ログイン',
                ip_address=request.remote_addr
            )
            
            print(f"DEBUG - 管理者ダッシュボードにリダイレクト")
            return redirect(url_for('super_user.dashboard'))
        else:
            print(f"DEBUG - 管理者ログイン失敗: {email}")
            flash('メールアドレスまたはパスワードが無効です', 'danger')
    
    return render_template('auth/admin_login.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # すでにログインしている場合はリダイレクト
    if current_user.is_authenticated:
        if current_user.user_type == UserType.TEACHER:
            return redirect(url_for('teacher.dashboard'))
        else:
            flash('講師アカウントでログインしてください', 'danger')
            logout_user()
            return redirect(url_for('auth.login'))
    
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        
        print(f"DEBUG - 講師ログイン試行: {email}")
        
        # スーパーユーザーが同じメールアドレスで存在するか確認
        super_user = SuperUser.query.filter_by(email=email).first()
        if super_user:
            print(f"DEBUG - 同じメールアドレスのスーパーユーザーが存在します: {email}")
            flash('このメールアドレスは管理者アカウントとして登録されています。管理者ログインページからログインしてください。', 'warning')
            return redirect(url_for('auth.admin_login'))
        
        # 講師のみ検索
        user = Teacher.query.filter_by(email=email).first()
        print(f"DEBUG - 講師検索結果: {user}")
        
        if user and user.check_password(password):
            print(f"DEBUG - 講師ログイン成功: {user.username}, ID: {user.id}")
            
            # ここで明示的にクラスをチェック
            if not isinstance(user, Teacher):
                print(f"DEBUG - 深刻な型エラー: {type(user)}")
                flash('アカウントタイプのエラーが発生しました', 'danger')
                return redirect(url_for('auth.login'))
            
            # カスタムIDを作成して保存
            user._id_with_prefix = f"T_{user.id}"
            print(f"DEBUG - カスタムID設定: {user._id_with_prefix}")
            
            login_user(user)
            
            # 最終ログイン時間を更新
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # ログを記録
            SystemLog.log_action(
                user_id=user.id,
                user_type=user.user_type,
                action='講師ログイン',
                ip_address=request.remote_addr
            )
            
            print(f"DEBUG - ダッシュボードにリダイレクト")
            return redirect(url_for('teacher.dashboard'))
        else:
            print(f"DEBUG - ログイン失敗: {email}")
            flash('メールアドレスまたはパスワードが無効です。あるいは、登録がありません。プレイグラウンドを利用したい方は、利用申請を行なってください。<a href="https://toieepartner.substack.com/p/ai-playground" target="_blank" style="text-decoration: underline; font-weight: bold;">詳しい情報はこちらです</a>', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    # ログを記録
    user_type = current_user.user_type
    SystemLog.log_action(
        user_id=current_user.id,
        user_type=user_type,
        action='ログアウト',
        ip_address=request.remote_addr
    )
    
    logout_user()
    flash('ログアウトしました', 'info')
    
    # ユーザータイプに応じて適切なログインページにリダイレクト
    if user_type == 'super_user':
        return redirect(url_for('auth.admin_login'))
    else:
        return redirect(url_for('auth.login'))