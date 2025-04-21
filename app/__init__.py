from flask import Flask
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
    
    # ホームページルート
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))
    
    return app