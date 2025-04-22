from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from functools import wraps
from flask import request, session, redirect, url_for

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

# ユーザータイプに基づいて適切なログインビューを設定するミドルウェア
@login_manager.unauthorized_handler
def unauthorized_handler():
    # URLに'admin'を含む場合は管理者ログインページにリダイレクト
    if '/admin' in request.path:
        login_manager.login_view = 'auth.admin_login'
    else:
        login_manager.login_view = 'auth.login'
    
    return redirect(url_for(login_manager.login_view))