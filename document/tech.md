# LibreChatユーザー管理システム - 技術仕様書

## 1. 技術要件

### 1.1 使用する言語やフレームワーク
- **プログラミング言語**: Python 3.9+
- **バックエンドフレームワーク**: Flask
- **フロントエンド**: Flask-Jinja2テンプレート + Bootstrap 5
- **データベース**: SQLite3
- **ORM**: SQLAlchemy

### 1.2 依存ライブラリやツール
- **Flask-Login**: ユーザー認証管理（バージョン: 0.6.2）- ユーザーセッション管理用
- **Flask-WTF**: フォーム処理とCSRF保護（バージョン: 1.1.1）- セキュアなフォーム処理用
- **subprocess**: LibreChatコマンド実行 - Python標準ライブラリ
- **SQLAlchemy**: データベース操作（バージョン: 2.0.x）- ORMとしてデータ操作用
- **python-dotenv**: 環境変数管理（バージョン: 1.0.0）- 設定情報の管理用
- **Werkzeug**: パスワードハッシュ化（Flask依存として含まれる）- セキュリティ確保用

### 1.3 デプロイ環境
- **開発環境**: ローカル開発環境（venv使用）
  - ローカルPC上で実行
  - 開発用サーバー（Flask内蔵）

- **本番環境**: LibreChatと同一サーバー上にデプロイ
  - Gunicorn + Nginx: 本番デプロイ用
  - systemdサービス: 自動起動と監視用

## 2. アプリケーション構成

### 2.1 システムアーキテクチャ
```
/librechat-user-manager/
  ├── app/                       # アプリケーションコード
  │   ├── __init__.py            # Flaskアプリケーション初期化
  │   ├── models/                # データモデル定義
  │   │   ├── __init__.py
  │   │   ├── user.py            # ユーザーモデル（SuperUser, Teacher, Student）
  │   │   └── logs.py            # システムログモデル
  │   ├── controllers/           # コントローラー
  │   │   ├── __init__.py
  │   │   ├── auth.py            # 認証関連
  │   │   ├── super_user.py      # スーパーユーザー機能
  │   │   ├── teacher.py         # 講師機能
  │   │   └── system.py          # システム管理機能
  │   ├── services/              # ビジネスロジック
  │   │   ├── __init__.py
  │   │   └── librechat.py       # LibreChatコマンド実行ラッパー
  │   ├── static/                # 静的ファイル（CSS, JS）
  │   └── templates/             # Jinja2テンプレート
  ├── config.py                  # 設定ファイル
  ├── .env                       # 環境変数（非Git管理）
  ├── requirements.txt           # 依存ライブラリ
  ├── run.py                     # アプリケーション起動スクリプト
  └── migrations/                # データベースマイグレーション
```

### 2.2 データベース設計
SQLiteを使用し、以下のテーブル構造を実装：

#### SuperUser（スーパーユーザー）
```sql
CREATE TABLE super_user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(100) UNIQUE NOT NULL,
    username VARCHAR(50) NOT NULL,
    password_hash VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

#### Teacher（講師）
```sql
CREATE TABLE teacher (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(100) UNIQUE NOT NULL,
    username VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(200) NOT NULL,
    prefix VARCHAR(50) NOT NULL,
    max_students INTEGER DEFAULT 20,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    created_by INTEGER,
    FOREIGN KEY (created_by) REFERENCES super_user(id)
);
```

#### Student（生徒）
```sql
CREATE TABLE student (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(100) UNIQUE NOT NULL,
    username VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    password VARCHAR(100) NOT NULL,  -- 非ハッシュ化（LibreChat連携用）
    teacher_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES teacher(id)
);
```

#### SystemLog（システムログ）
```sql
CREATE TABLE system_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER,
    user_type VARCHAR(20),  -- 'super_user' or 'teacher'
    action VARCHAR(100) NOT NULL,
    details TEXT,
    ip_address VARCHAR(50)
);
```

## 3. コア機能実装

### 3.1 LibreChat操作ラッパー
```python
class LibreChatService:
    def __init__(self, librechat_root):
        self.librechat_root = librechat_root
    
    def create_user(self, email, username, name, password):
        """ユーザーを作成する"""
        # コマンドインジェクション対策のためにshlex.quoteを使用
        cmd = f"npm run create-user {shlex.quote(email)} {shlex.quote(username)} {shlex.quote(name)} {shlex.quote(password)} --email-verified=true"
        return self._run_command(cmd)
    
    def delete_user(self, email):
        """ユーザーを削除する"""
        cmd = f"npm run delete-user {shlex.quote(email)}"
        return self._run_command(cmd)
    
    def list_users(self):
        """ユーザー一覧を取得する"""
        cmd = "npm run list-users"
        result = self._run_command(cmd)
        return self._parse_user_list(result.stdout)
    
    def _run_command(self, cmd):
        """コマンドを実行する"""
        return subprocess.run(cmd, shell=True, cwd=self.librechat_root, 
                             capture_output=True, text=True)
    
    def _parse_user_list(self, output):
        """コマンド出力からユーザー一覧を解析する"""
        # 実装はLibreChatの出力形式に依存
        users = []
        # 出力解析ロジック
        return users
```

### 3.2 認証機能
```python
# app/controllers/auth.py
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # SuperUserとTeacherの両方からユーザー検索
        user = SuperUser.query.filter_by(email=form.email.data).first()
        if not user:
            user = Teacher.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user)
            # ユーザータイプに基づいてリダイレクト
            if isinstance(user, SuperUser):
                return redirect(url_for('super_user.dashboard'))
            else:
                return redirect(url_for('teacher.dashboard'))
        else:
            flash('メールアドレスまたはパスワードが無効です', 'danger')
    
    return render_template('auth/login.html', form=form)
```

### 3.3 講師機能（生徒アカウント一括作成）
```python
# app/controllers/teacher.py
@teacher_bp.route('/students/bulk-create', methods=['GET', 'POST'])
@login_required
@teacher_required
def bulk_create_students():
    form = BulkCreateStudentForm()
    if form.validate_on_submit():
        # フォームデータを解析
        prefix = current_user.prefix
        count = form.count.data
        password = form.password.data or generate_password()
        
        created_students = []
        librechat = LibreChatService(current_app.config['LIBRECHAT_ROOT'])
        
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
            name = f"Student {i:02d}"
            
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
            log_action(current_user.id, 'teacher', f'{len(created_students)}件の生徒アカウントを作成', 
                      details=f"Prefix: {prefix}, Count: {count}")
            flash(f'{len(created_students)}件の生徒アカウントを作成しました', 'success')
        
        return redirect(url_for('teacher.list_students'))
    
    return render_template('teacher/bulk_create_students.html', form=form)
```

## 4. セキュリティ実装

### 4.1 認証・認可
- Flask-Loginによるセッション管理
- パスワードはWerkzeugを使用してbcryptでハッシュ化
- ロールベースのアクセス制御（スーパーユーザー、講師）
- CSRF保護（Flask-WTF）

### 4.2 入力検証
- すべてのフォーム入力はサーバーサイドで検証
- コマンドインジェクション対策（shlex.quote使用）
- XSS対策（Jinja2のエスケープ機能）

### 4.3 ログ記録
- すべての操作はシステムログに記録
- エラー発生時は詳細をログに記録
- アクセスIPアドレスを記録

## 5. デプロイとメンテナンス

### 5.1 デプロイ手順
1. コードをサーバーにクローン
2. 仮想環境を作成し、依存関係をインストール
3. `.env`ファイルで環境設定
4. データベースの初期化
5. Gunicorn + Nginxの設定
6. systemdサービスの設定

### 5.2 バックアップ
- SQLiteデータベースファイルの定期バックアップ
- cronジョブでの自動バックアップ設定

### 5.3 更新・メンテナンス
- システム更新手順
- データベースマイグレーション方法
- トラブルシューティングガイド

## 6. テスト計画

### 6.1 ユニットテスト
- モデルテスト
- サービステスト（LibreChatコマンド実行モック）

### 6.2 統合テスト
- 認証フロー
- ユーザー管理フロー
- エラー処理

### 6.3 手動テスト
- ブラウザ互換性テスト
- ユーザーロールごとの操作確認