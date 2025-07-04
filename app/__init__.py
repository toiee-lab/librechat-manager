from flask import Flask, redirect, url_for, request
from flask_wtf.csrf import CSRFProtect

from app.models import db, login_manager
from app.controllers.auth import auth_bp
from app.controllers.super_user import super_user_bp
from app.controllers.teacher import teacher_bp
from app.controllers.system import system_bp

csrf = CSRFProtect()

def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 拡張機能の初期化
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # ブループリントの登録
    app.register_blueprint(auth_bp)
    app.register_blueprint(super_user_bp, url_prefix='/admin')
    app.register_blueprint(teacher_bp, url_prefix='/teacher')
    app.register_blueprint(system_bp)
    
    # ルートディレクトリでのデプロイ - URLプロセッサは不要
    
    # ホームページルート
    @app.route('/')
    def index():
        from flask_login import current_user
        
        # ログイン状態とユーザータイプに応じて適切にリダイレクト
        if current_user.is_authenticated:
            if current_user.user_type == 'super_user':
                return redirect(url_for('super_user.dashboard'))
            elif current_user.user_type == 'teacher':
                return redirect(url_for('teacher.dashboard'))
        
        # 未ログイン時は講師ログインページにリダイレクト
        return redirect(url_for('auth.login'))
        
    @app.route('/admin')
    def admin():
        from flask_login import current_user
        
        # ログイン状態とユーザータイプに応じて適切にリダイレクト
        if current_user.is_authenticated and current_user.user_type == 'super_user':
            return redirect(url_for('super_user.dashboard'))
        
        # 未ログインまたはスーパーユーザーでない場合は管理者ログインページにリダイレクト
        return redirect(url_for('auth.admin_login'))
    
    return app