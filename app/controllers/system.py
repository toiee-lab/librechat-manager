from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from functools import wraps

from app.models.user import UserType
from app.models.logs import SystemLog
from app.controllers.super_user import super_user_required

system_bp = Blueprint('system', __name__)

@system_bp.route('/system/logs')
@login_required
@super_user_required
def system_logs():
    page = request.args.get('page', 1, type=int)
    
    # 検索条件
    user_type = request.args.get('user_type')
    action = request.args.get('action')
    
    # ベースクエリ
    query = SystemLog.query
    
    # フィルタ適用
    if user_type:
        query = query.filter(SystemLog.user_type == user_type)
    if action:
        query = query.filter(SystemLog.action.like(f'%{action}%'))
    
    # 並び替えと取得
    logs = query.order_by(SystemLog.timestamp.desc()).paginate(
        page=page, per_page=20, error_out=False)
    
    # ログに記録
    SystemLog.log_action(
        user_id=current_user.id,
        user_type=current_user.user_type,
        action='システムログを閲覧',
        ip_address=request.remote_addr
    )
    
    return render_template('system/logs.html', logs=logs)