import csv
import io
import random
import string
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, Response
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from functools import wraps

from app.models.user import Teacher, Student, UserType
from app.models.logs import SystemLog
from app.models import db
from app.services.librechat import LibreChatService

teacher_bp = Blueprint('teacher', __name__)

# 講師権限チェック用デコレータ
def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # デバッグ情報をログに出力
        print(f"DEBUG - 認証状態: {current_user.is_authenticated}")
        
        if not current_user.is_authenticated:
            flash('ログインが必要です', 'danger')
            return redirect(url_for('auth.login'))
        
        # user_typeが取得できるか確認
        try:
            from app.models.user import Teacher
            # インスタンスの型を直接チェック
            is_teacher = isinstance(current_user, Teacher)
            print(f"DEBUG - ユーザークラス: {current_user.__class__.__name__}")
            print(f"DEBUG - Teacher型チェック: {is_teacher}")
            
            if not is_teacher:
                print(f"DEBUG - ユーザータイプ比較失敗")
                flash('この操作には講師権限が必要です', 'danger')
                return redirect(url_for('auth.login'))
                
        except Exception as e:
            print(f"DEBUG - 例外発生: {str(e)}")
            flash('アクセス権限の確認中にエラーが発生しました', 'danger')
            return redirect(url_for('auth.login'))
            
        return f(*args, **kwargs)
    return decorated_function

class BulkCreateStudentForm(FlaskForm):
    count = IntegerField('生徒アカウント数', validators=[
        DataRequired(),
        NumberRange(min=1, max=20, message='生徒数は1〜20の間で指定してください')
    ])
    password = StringField('パスワード（空欄の場合は自動生成）')
    submit = SubmitField('アカウント作成')

def generate_password(length=8):
    """ランダムパスワードを生成する"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@teacher_bp.route('/dashboard')
@login_required
@teacher_required
def dashboard():
    students_count = Student.query.filter_by(teacher_id=current_user.id).count()
    return render_template('teacher/dashboard.html', students_count=students_count)

@teacher_bp.route('/students')
@login_required
@teacher_required
def list_students():
    students = Student.query.filter_by(teacher_id=current_user.id).all()
    return render_template('teacher/students.html', students=students)

@teacher_bp.route('/students/bulk-create', methods=['GET', 'POST'])
@login_required
@teacher_required
def bulk_create_students():
    form = BulkCreateStudentForm()
    if form.validate_on_submit():
        # フォームデータを解析
        prefix = current_user.prefix
        count = form.count.data
        common_password = form.password.data
        
        created_students = []
        librechat = LibreChatService(
            current_app.config['LIBRECHAT_ROOT'],
            container_name=current_app.config['LIBRECHAT_CONTAINER'],
            work_dir=current_app.config['LIBRECHAT_WORK_DIR'],
            docker_path=current_app.config['DOCKER_PATH']
        )
        
        # 既存の学生数をチェック
        existing_count = Student.query.filter_by(teacher_id=current_user.id).count()
        if existing_count + count > current_user.max_students:
            flash(f'作成可能な生徒数を超えています（最大: {current_user.max_students}）', 'danger')
            return redirect(url_for('teacher.bulk_create_students'))
        
        # 学生アカウントを作成
        for i in range(1, count + 1):
            # 連番形式のメールアドレスとユーザー名を生成
            email = f"{prefix}{i:02d}@toiee.jp"
            username = f"{prefix}{i:02d}"
            name = f"{prefix}{i:02d}"
            
            # 各ユーザーごとに個別のランダムパスワードを生成
            password = common_password or generate_password()
            
            # 既存アカウントを確認
            existing = Student.query.filter_by(email=email).first()
            if existing:
                flash(f'メールアドレス {email} は既に使用されています', 'warning')
                continue
            
            # LibreChatにユーザーを作成
            result = librechat.create_user(email, username, name, password)
            
            if result.returncode == 0:
                # 成功した場合、DBに記録
                student = Student(
                    email=email,
                    username=username,
                    name=name,
                    password=password,  # 注: 非ハッシュ化して保存
                    teacher_id=current_user.id
                )
                db.session.add(student)
                created_students.append(student)
            else:
                # エラーがあれば記録
                flash(f'ユーザー {email} の作成中にエラーが発生しました', 'danger')
                # ログに詳細を記録
        
        if created_students:
            db.session.commit()
            # システムログに記録
            SystemLog.log_action(
                user_id=current_user.id,
                user_type=UserType.TEACHER,
                action=f'{len(created_students)}件の生徒アカウントを作成',
                details=f"Prefix: {prefix}, Count: {count}",
                ip_address=request.remote_addr
            )
            flash(f'{len(created_students)}件の生徒アカウントを作成しました', 'success')
            return redirect(url_for('teacher.list_students'))
    
    return render_template('teacher/bulk_create_students.html', form=form)

@teacher_bp.route('/students/reset', methods=['GET', 'POST'])
@login_required
@teacher_required
def reset_students():
    if request.method == 'POST':
        # 確認チェック
        confirm = request.form.get('confirm')
        if not confirm or confirm != 'yes':
            flash('確認チェックが必要です', 'warning')
            return redirect(url_for('teacher.reset_students'))
        
        librechat = LibreChatService(
            current_app.config['LIBRECHAT_ROOT'],
            container_name=current_app.config['LIBRECHAT_CONTAINER'],
            work_dir=current_app.config['LIBRECHAT_WORK_DIR'],
            docker_path=current_app.config['DOCKER_PATH']
        )
        students = Student.query.filter_by(teacher_id=current_user.id).all()
        
        # 既存アカウントを削除
        for student in students:
            # LibreChatからユーザーを削除
            librechat.delete_user(student.email)
        
        # DBから削除
        Student.query.filter_by(teacher_id=current_user.id).delete()
        db.session.commit()
        
        # システムログに記録
        SystemLog.log_action(
            user_id=current_user.id,
            user_type=UserType.TEACHER,
            action='全生徒アカウントをリセット',
            details=f"アカウント数: {len(students)}",
            ip_address=request.remote_addr
        )
        
        flash('全ての生徒アカウントをリセットしました', 'success')
        return redirect(url_for('teacher.bulk_create_students'))
    
    return render_template('teacher/reset_students.html')

@teacher_bp.route('/students/export-csv')
@login_required
@teacher_required
def export_students_csv():
    students = Student.query.filter_by(teacher_id=current_user.id).all()
    
    # CSVファイルを生成
    output = io.StringIO()
    writer = csv.writer(output)
    
    # ヘッダー行
    writer.writerow(['メールアドレス', 'パスワード'])
    
    # データ行
    for student in students:
        writer.writerow([student.email, student.password])
    
    # システムログに記録
    SystemLog.log_action(
        user_id=current_user.id,
        user_type=UserType.TEACHER,
        action='生徒アカウント情報をCSVエクスポート',
        ip_address=request.remote_addr
    )
    
    # CSVレスポンスを返す
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=students.csv'}
    )