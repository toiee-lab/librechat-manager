# LibreChatユーザー管理システム

LibreChatを活用したAI授業・ワークショップでのユーザーアカウント管理を効率化するためのWebアプリケーションです。

## 主な機能

### スーパーユーザー機能
- 講師アカウントの追加・編集・削除
- 講師ごとのプレフィックス、最大ユーザー作成数の設定
- システム操作ログの閲覧

### 講師向け機能
- 生徒アカウントの一括作成（プレフィックスXX@toiee.jp形式）
- 生徒アカウントの一括リセット（削除と再作成）
- 生徒アカウント情報の一覧表示・CSVエクスポート

## 技術スタック

- **バックエンド**: Python 3.9+、Flask
- **フロントエンド**: Bootstrap 5、Jinja2テンプレート
- **データベース**: SQLite3（SQLAlchemy ORM）
- **認証**: Flask-Login
- **セキュリティ**: Flask-WTF（CSRF保護）

## インストール手順

### 前提条件
- Python 3.9以上
- LibreChatがインストールされたサーバー

### セットアップ
1. リポジトリをクローン
   ```
   git clone https://github.com/yourusername/librechat-user-manager.git
   cd librechat-user-manager
   ```

2. 仮想環境を作成し、依存関係をインストール
   ```
   python -m venv venv
   source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. 環境設定ファイルを作成
   ```
   cp .env.example .env
   ```
   `.env`ファイルを編集し、必要な設定（特にLIBRECHAT_ROOTのパス）を行います。

4. データベースを初期化
   ```
   flask create-db
   ```

5. スーパーユーザーを作成
   ```
   flask create-super-user
   ```

6. アプリケーションを起動
   ```
   flask run
   ```

## 本番環境へのデプロイ

本番環境では、以下の設定を推奨します：

1. Gunicorn + Nginxを使用
   ```
   gunicorn -w 4 -b 127.0.0.1:8000 "run:app"
   ```

2. systemdサービスとして設定
   ```
   [Unit]
   Description=LibreChat User Manager
   After=network.target

   [Service]
   User=yourusername
   WorkingDirectory=/path/to/librechat-user-manager
   Environment="PATH=/path/to/librechat-user-manager/venv/bin"
   ExecStart=/path/to/librechat-user-manager/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 "run:app"
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

## 使用方法

1. スーパーユーザーでログイン
2. 講師アカウントを作成（プレフィックスを設定）
3. 講師アカウントでログインし、生徒アカウントを作成
4. 必要に応じて生徒アカウントをリセット

## ライセンス

MITライセンスの下で公開されています。詳細はLICENSEファイルを参照してください。