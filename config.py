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
    
    # セッションクッキー設定（LibreChatとの競合を回避）
    # Werkzeug 3.x + Python 3.13での互換性問題を回避するため、パス設定を無効化
    SESSION_COOKIE_PATH = None
    
    def __init__(self):
        """セッションクッキー名をアプリケーション固有に設定"""
        super().__init__()
        if self.APPLICATION_ROOT and self.APPLICATION_ROOT != '/':
            # サブパスの場合、パス名を基にクッキー名を生成
            path_name = self.APPLICATION_ROOT.strip('/').replace('/', '_')
            self.SESSION_COOKIE_NAME = f'lft_{path_name}_session'
        else:
            self.SESSION_COOKIE_NAME = 'lft_session'
    
    # LibreChat設定
    LIBRECHAT_ROOT = os.environ.get('LIBRECHAT_ROOT') or '/path/to/librechat'
    LIBRECHAT_CONTAINER = os.environ.get('LIBRECHAT_CONTAINER') or 'LibreChat'
    LIBRECHAT_WORK_DIR = os.environ.get('LIBRECHAT_WORK_DIR') or '.'
    DOCKER_PATH = os.environ.get('DOCKER_PATH') or '/usr/bin/docker'