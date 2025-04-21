from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.models import db, login_manager

class UserType:
    SUPER_USER = 'super_user'
    TEACHER = 'teacher'
    STUDENT = 'student'

class SuperUser(db.Model, UserMixin):
    __tablename__ = 'super_user'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def user_type(self):
        return UserType.SUPER_USER

class Teacher(db.Model, UserMixin):
    __tablename__ = 'teacher'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    prefix = db.Column(db.String(50), nullable=False)
    max_students = db.Column(db.Integer, default=20)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('super_user.id'))
    
    students = db.relationship('Student', backref='teacher', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def user_type(self):
        return UserType.TEACHER

class Student(db.Model):
    __tablename__ = 'student'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)  # 非ハッシュ化
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    # IDの形式から適切なユーザーモデルを選択
    if user_id.startswith('s_'):
        user_id = user_id[2:]
        return SuperUser.query.get(int(user_id))
    elif user_id.startswith('t_'):
        user_id = user_id[2:]
        return Teacher.query.get(int(user_id))
    return None

# ユーザー取得用ヘルパー関数
def get_user_by_email(email):
    user = SuperUser.query.filter_by(email=email).first()
    if not user:
        user = Teacher.query.filter_by(email=email).first()
    return user