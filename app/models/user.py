from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.models import db, login_manager

class UserType:
    SUPER_USER = 'super_user'
    TEACHER = 'teacher'
    STUDENT = 'student'

# カスタムUserMixinクラスで、get_idをオーバーライド
class CustomUserMixin(UserMixin):
    _id_with_prefix = None
    
    def get_id(self):
        """IDを取得するメソッド"""
        try:
            # カスタムIDがある場合はそれを使用
            if hasattr(self, '_id_with_prefix') and self._id_with_prefix:
                print(f"DEBUG - get_id: カスタムID {self._id_with_prefix}")
                return str(self._id_with_prefix)
            
            # なければ通常のID
            if hasattr(self, 'id'):
                print(f"DEBUG - get_id: 通常ID {self.id}")
                return str(self.id)
            
            print("DEBUG - get_id: IDなし")
            return None
        except Exception as e:
            print(f"DEBUG - get_id エラー: {str(e)}")
            return None

class SuperUser(db.Model, CustomUserMixin):
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

class Teacher(db.Model, CustomUserMixin):
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
    try:
        # ユーザーIDにプレフィックスがある場合は処理
        if isinstance(user_id, str) and user_id.startswith('S_'):
            # スーパーユーザーのID
            real_id = int(user_id[2:])
            print(f"DEBUG - load_user: SuperUser ID {real_id}を検索")
            return SuperUser.query.get(real_id)
        elif isinstance(user_id, str) and user_id.startswith('T_'):
            # 講師のID
            real_id = int(user_id[2:])
            print(f"DEBUG - load_user: Teacher ID {real_id}を検索")
            return Teacher.query.get(real_id)
        
        # プレフィックスがない場合（既存のコード互換性のため）
        # この部分は必要に応じて後で削除できる
        uid = int(user_id)
        print(f"DEBUG - load_user: レガシーモード ID {uid}を検索")
        
        # 両方のモデルを検索 - インスタンスを返す前に型をチェック
        user = SuperUser.query.get(uid)
        if user:
            print(f"DEBUG - load_user: SuperUser見つかりました {user.username}")
            return user
        
        user = Teacher.query.get(uid)
        if user:
            print(f"DEBUG - load_user: Teacher見つかりました {user.username}")
            return user
        
        print(f"DEBUG - load_user: ユーザー未発見 ID {user_id}")
        return None
    except Exception as e:
        print(f"DEBUG - load_user エラー: {str(e)}")
        return None

# この関数は廃止予定 - 代わりに直接モデルのクエリを使用する
def get_user_by_email(email):
    print(f"WARNING - 非推奨の get_user_by_email 関数が呼ばれました: {email}")
    return None