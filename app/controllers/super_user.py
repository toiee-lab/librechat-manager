from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError, Length, Regexp
from functools import wraps

from app.models.user import SuperUser, Teacher, UserType
from app.models.logs import SystemLog
from app.models import db
from app.services.librechat import LibreChatService

super_user_bp = Blueprint('super_user', __name__)

# スーパーユーザー権限チェック用デコレータ
def super_user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # デバッグ情報をログに出力
        print(f"DEBUG - 認証状態: {current_user.is_authenticated}")
        
        if not current_user.is_authenticated:
            flash('ログインが必要です', 'danger')
            return redirect(url_for('auth.admin_login'))
        
        # user_typeが取得できるか確認
        try:
            from app.models.user import SuperUser
            # インスタンスの型を直接チェック
            is_super_user = isinstance(current_user, SuperUser)
            print(f"DEBUG - ユーザークラス: {current_user.__class__.__name__}")
            print(f"DEBUG - SuperUser型チェック: {is_super_user}")
            
            if not is_super_user:
                print(f"DEBUG - ユーザータイプ比較失敗")
                flash('この操作にはスーパーユーザー権限が必要です', 'danger')
                return redirect(url_for('auth.admin_login'))
                
        except Exception as e:
            print(f"DEBUG - 例外発生: {str(e)}")
            flash('アクセス権限の確認中にエラーが発生しました', 'danger')
            return redirect(url_for('auth.admin_login'))
            
        return f(*args, **kwargs)
    return decorated_function

class TeacherForm(FlaskForm):
    email = StringField('メールアドレス', validators=[DataRequired(), Email()])
    username = StringField('ユーザー名', validators=[
        DataRequired(),
        Regexp('^[A-Za-z0-9]+$', message='ユーザー名は半角英数字のみ使用できます')
    ])
    name = StringField('氏名', validators=[DataRequired()])
    password = PasswordField('パスワード', validators=[DataRequired(), Length(min=8)])
    prefix = StringField('プレフィックス', validators=[
        DataRequired(), 
        Length(min=2, max=10),
        Regexp('^[a-z]+$', message='プレフィックスは半角英小文字のみ使用できます')
    ])
    max_students = IntegerField('最大生徒数', default=20)
    submit = SubmitField('保存')
    
    def validate_email(self, email):
        user = Teacher.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('このメールアドレスは既に使用されています')
        
        super_user = SuperUser.query.filter_by(email=email.data).first()
        if super_user:
            raise ValidationError('このメールアドレスは既に使用されています')
    
    def validate_prefix(self, prefix):
        teacher = Teacher.query.filter_by(prefix=prefix.data).first()
        if teacher:
            raise ValidationError('このプレフィックスは既に使用されています')

class EditTeacherForm(FlaskForm):
    name = StringField('氏名', validators=[DataRequired()])
    max_students = IntegerField('最大生徒数', default=20)
    password = PasswordField('新しいパスワード（変更する場合のみ）')
    submit = SubmitField('更新')

@super_user_bp.route('/dashboard')
@login_required
@super_user_required
def dashboard():
    teachers_count = Teacher.query.count()
    return render_template('super_user/dashboard.html', teachers_count=teachers_count)

@super_user_bp.route('/teachers')
@login_required
@super_user_required
def list_teachers():
    teachers = Teacher.query.all()
    return render_template('super_user/teachers.html', teachers=teachers)

@super_user_bp.route('/teachers/create', methods=['GET', 'POST'])
@login_required
@super_user_required
def create_teacher():
    form = TeacherForm()
    if form.validate_on_submit():
        teacher = Teacher(
            email=form.email.data,
            username=form.username.data,
            name=form.name.data,
            prefix=form.prefix.data,
            max_students=form.max_students.data,
            created_by=current_user.id
        )
        teacher.set_password(form.password.data)
        
        db.session.add(teacher)
        db.session.commit()
        
        # LibreChatでもユーザーを作成
        try:
            librechat_service = LibreChatService(
                current_app.config['LIBRECHAT_ROOT'],
                container_name=current_app.config['LIBRECHAT_CONTAINER'],
                work_dir=current_app.config['LIBRECHAT_WORK_DIR'],
                docker_path=current_app.config['DOCKER_PATH']
            )
            librechat_result = librechat_service.create_user(
                email=teacher.email,
                username=teacher.username,
                name=teacher.name,
                password=form.password.data
            )
            if librechat_result.returncode == 0:
                librechat_status = "成功"
            else:
                librechat_status = f"失敗 (エラー: {librechat_result.stderr})"
        except Exception as e:
            librechat_status = f"エラー: {str(e)}"
        
        SystemLog.log_action(
            user_id=current_user.id,
            user_type=UserType.SUPER_USER,
            action='講師アカウント作成',
            details=f"Email: {teacher.email}, Name: {teacher.name}, Prefix: {teacher.prefix}, LibreChat: {librechat_status}",
            ip_address=request.remote_addr
        )
        
        flash(f'講師アカウント「{teacher.name}」を作成しました', 'success')
        return redirect(url_for('super_user.list_teachers'))
    
    return render_template('super_user/create_teacher.html', form=form)

@super_user_bp.route('/teachers/<int:teacher_id>/edit', methods=['GET', 'POST'])
@login_required
@super_user_required
def edit_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    form = EditTeacherForm(obj=teacher)
    
    if form.validate_on_submit():
        teacher.name = form.name.data
        teacher.max_students = form.max_students.data
        
        if form.password.data:
            teacher.set_password(form.password.data)
        
        db.session.commit()
        
        SystemLog.log_action(
            user_id=current_user.id,
            user_type=UserType.SUPER_USER,
            action='講師アカウント編集',
            details=f"ID: {teacher.id}, Name: {teacher.name}",
            ip_address=request.remote_addr
        )
        
        flash(f'講師アカウント「{teacher.name}」を更新しました', 'success')
        return redirect(url_for('super_user.list_teachers'))
    
    return render_template('super_user/edit_teacher.html', form=form, teacher=teacher)

@super_user_bp.route('/teachers/<int:teacher_id>/delete', methods=['POST'])
@login_required
@super_user_required
def delete_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    teacher_name = teacher.name
    teacher_email = teacher.email
    
    # 講師が作成した生徒一覧を取得
    students = teacher.students.all()
    deleted_students = []
    
    # LibreChatサービスのインスタンス作成
    librechat_service = LibreChatService(
        current_app.config['LIBRECHAT_ROOT'],
        container_name=current_app.config['LIBRECHAT_CONTAINER'],
        work_dir=current_app.config['LIBRECHAT_WORK_DIR'],
        docker_path=current_app.config['DOCKER_PATH']
    )
    
    # 各生徒のLibreChatユーザーを削除
    for student in students:
        try:
            result = librechat_service.delete_user(email=student.email)
            status = "成功" if result.returncode == 0 else f"失敗 ({result.stderr})"
        except Exception as e:
            status = f"エラー: {str(e)}"
        
        deleted_students.append(f"{student.name} ({student.email}): {status}")
    
    # 講師のLibreChatユーザーを削除
    try:
        librechat_service = LibreChatService(
            current_app.config['LIBRECHAT_ROOT'],
            container_name=current_app.config['LIBRECHAT_CONTAINER'],
            work_dir=current_app.config['LIBRECHAT_WORK_DIR'],
            docker_path=current_app.config['DOCKER_PATH']
        )
        librechat_result = librechat_service.delete_user(email=teacher_email)
        teacher_librechat_status = "成功" if librechat_result.returncode == 0 else f"失敗 ({librechat_result.stderr})"
    except Exception as e:
        teacher_librechat_status = f"エラー: {str(e)}"
    
    # 関連する生徒を先に削除する
    for student in students:
        db.session.delete(student)
    
    # 講師を削除
    db.session.delete(teacher)
    db.session.commit()
    
    # ログ記録
    log_details = f"ID: {teacher_id}, Name: {teacher_name}, Email: {teacher_email}, LibreChat: {teacher_librechat_status}"
    if deleted_students:
        log_details += f", 削除された生徒: {len(deleted_students)}名"
    
    SystemLog.log_action(
        user_id=current_user.id,
        user_type=UserType.SUPER_USER,
        action='講師アカウント削除',
        details=log_details,
        ip_address=request.remote_addr
    )
    
    flash(f'講師アカウント「{teacher_name}」と関連する生徒アカウント（{len(deleted_students)}名）を削除しました', 'success')
    return redirect(url_for('super_user.list_teachers'))

@super_user_bp.route('/users')
@login_required
@super_user_required
def user_management():
    return render_template('super_user/user_management.html')

@super_user_bp.route('/api/users', methods=['GET'])
@login_required
@super_user_required
def api_get_users():
    try:
        # LibreChatServiceを使用してユーザー一覧を取得
        librechat_service = LibreChatService(
            current_app.config['LIBRECHAT_ROOT'],
            container_name=current_app.config['LIBRECHAT_CONTAINER'],
            work_dir=current_app.config['LIBRECHAT_WORK_DIR'],
            docker_path=current_app.config['DOCKER_PATH']
        )
        
        users = librechat_service.list_users()
        
        # 講師別にグループ化
        grouped_users = _group_users_by_teacher(users)
        
        # システムログに記録
        SystemLog.log_action(
            user_id=current_user.id,
            user_type=UserType.SUPER_USER,
            action='LibreChatユーザー一覧取得',
            details=f"取得件数: {len(users)}件",
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'success': True,
            'users': users,
            'grouped_users': grouped_users,
            'count': len(users)
        })
        
    except Exception as e:
        # エラーログに記録
        SystemLog.log_action(
            user_id=current_user.id,
            user_type=UserType.SUPER_USER,
            action='LibreChatユーザー一覧取得エラー',
            details=f"エラー: {str(e)}",
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def _group_users_by_teacher(users):
    """ユーザーを講師別にグループ化する"""
    # データベースから講師一覧を取得
    teachers = Teacher.query.all()
    teacher_prefixes = {teacher.prefix: teacher for teacher in teachers}
    teacher_emails = {teacher.email: teacher for teacher in teachers}
    
    grouped = {
        'teachers': {},
        'others': []
    }
    
    for user in users:
        username = user.get('username', '')
        email = user.get('email', '')
        
        # 講師アカウントかどうかをチェック
        is_teacher = email in teacher_emails
        user['is_teacher'] = is_teacher
        
        # プレフィックスを判定
        matched_teacher = None
        for prefix, teacher in teacher_prefixes.items():
            # ユーザー名またはメールアドレスがプレフィックスで始まるかチェック
            if username.startswith(prefix) or email.startswith(prefix):
                matched_teacher = teacher
                break
        
        if matched_teacher:
            teacher_key = f"{matched_teacher.name} ({matched_teacher.prefix})"
            if teacher_key not in grouped['teachers']:
                grouped['teachers'][teacher_key] = {
                    'teacher_info': {
                        'id': matched_teacher.id,
                        'name': matched_teacher.name,
                        'prefix': matched_teacher.prefix,
                        'email': matched_teacher.email
                    },
                    'users': []
                }
            grouped['teachers'][teacher_key]['users'].append(user)
        else:
            grouped['others'].append(user)
    
    return grouped

@super_user_bp.route('/api/users/delete', methods=['POST'])
@login_required
@super_user_required
def api_delete_user():
    try:
        print(f"DEBUG - Request content type: {request.content_type}")
        print(f"DEBUG - Request data: {request.data}")
        
        data = request.get_json()
        print(f"DEBUG - Parsed JSON data: {data}")
        
        if not data or 'email' not in data:
            return jsonify({
                'success': False,
                'error': 'メールアドレスが指定されていません',
                'debug_info': {
                    'data': data,
                    'content_type': request.content_type
                }
            }), 400
        
        email = data['email']
        
        # まず講師アカウントかどうかをチェック
        teacher = Teacher.query.filter_by(email=email).first()
        if teacher:
            return jsonify({
                'success': False,
                'error': '講師アカウントは削除できません'
            }), 400
        
        # LibreChatServiceを使用してユーザーを削除
        librechat_service = LibreChatService(
            current_app.config['LIBRECHAT_ROOT'],
            container_name=current_app.config['LIBRECHAT_CONTAINER'],
            work_dir=current_app.config['LIBRECHAT_WORK_DIR'],
            docker_path=current_app.config['DOCKER_PATH']
        )
        
        result = librechat_service.delete_user(email)
        
        if result.returncode == 0:
            # 成功時のログ記録
            SystemLog.log_action(
                user_id=current_user.id,
                user_type=UserType.SUPER_USER,
                action='LibreChatユーザー削除成功',
                details=f"削除されたユーザー: {email}",
                ip_address=request.remote_addr
            )
            
            return jsonify({
                'success': True,
                'message': f'ユーザー「{email}」を削除しました'
            })
        else:
            # 失敗時のログ記録
            error_msg = result.stderr or 'Unknown error'
            SystemLog.log_action(
                user_id=current_user.id,
                user_type=UserType.SUPER_USER,
                action='LibreChatユーザー削除失敗',
                details=f"削除対象: {email}, エラー: {error_msg}",
                ip_address=request.remote_addr
            )
            
            return jsonify({
                'success': False,
                'error': f'ユーザーの削除に失敗しました: {error_msg}'
            }), 500
        
    except Exception as e:
        # エラーログに記録
        email_for_log = 'Unknown'
        try:
            data = request.get_json() or {}
            email_for_log = data.get('email', 'Unknown')
        except:
            pass
            
        SystemLog.log_action(
            user_id=current_user.id,
            user_type=UserType.SUPER_USER,
            action='LibreChatユーザー削除エラー',
            details=f"削除対象: {email_for_log}, エラー: {str(e)}",
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@super_user_bp.route('/logs')
@login_required
@super_user_required
def view_logs():
    page = request.args.get('page', 1, type=int)
    logs = SystemLog.query.order_by(SystemLog.timestamp.desc()).paginate(
        page=page, per_page=20, error_out=False)
    
    return render_template('super_user/logs.html', logs=logs)