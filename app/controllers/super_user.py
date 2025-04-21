from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError, Length
from functools import wraps

from app.models.user import SuperUser, Teacher, UserType
from app.models.logs import SystemLog
from app.models import db

super_user_bp = Blueprint('super_user', __name__)

# スーパーユーザー権限チェック用デコレータ
def super_user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.user_type != UserType.SUPER_USER:
            flash('この操作にはスーパーユーザー権限が必要です', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

class TeacherForm(FlaskForm):
    email = StringField('メールアドレス', validators=[DataRequired(), Email()])
    username = StringField('ユーザー名', validators=[DataRequired()])
    name = StringField('氏名', validators=[DataRequired()])
    password = PasswordField('パスワード', validators=[DataRequired(), Length(min=8)])
    prefix = StringField('プレフィックス', validators=[DataRequired(), Length(min=2, max=10)])
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
        
        SystemLog.log_action(
            user_id=current_user.id,
            user_type=UserType.SUPER_USER,
            action='講師アカウント作成',
            details=f"Email: {teacher.email}, Name: {teacher.name}, Prefix: {teacher.prefix}",
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
    
    db.session.delete(teacher)
    db.session.commit()
    
    SystemLog.log_action(
        user_id=current_user.id,
        user_type=UserType.SUPER_USER,
        action='講師アカウント削除',
        details=f"ID: {teacher_id}, Name: {teacher_name}",
        ip_address=request.remote_addr
    )
    
    flash(f'講師アカウント「{teacher_name}」を削除しました', 'success')
    return redirect(url_for('super_user.list_teachers'))

@super_user_bp.route('/logs')
@login_required
@super_user_required
def view_logs():
    page = request.args.get('page', 1, type=int)
    logs = SystemLog.query.order_by(SystemLog.timestamp.desc()).paginate(
        page=page, per_page=20, error_out=False)
    
    return render_template('super_user/logs.html', logs=logs)