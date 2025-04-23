import os
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

class Config:
    # アプリケーション設定
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-replace-in-production'
    
    # データベース設定
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # アプリケーションルートパス設定（サブフォルダデプロイメント用）
    APPLICATION_ROOT = os.environ.get('APPLICATION_ROOT') or '/'
    
    # LibreChat設定
    LIBRECHAT_ROOT = os.environ.get('LIBRECHAT_ROOT') or '/path/to/librechat'
    LIBRECHAT_CONTAINER = os.environ.get('LIBRECHAT_CONTAINER') or 'LibreChat'
    LIBRECHAT_WORK_DIR = os.environ.get('LIBRECHAT_WORK_DIR') or '.'
    DOCKER_PATH = os.environ.get('DOCKER_PATH') or '/usr/bin/docker'