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
    @property
    def SESSION_COOKIE_PATH(self):
        """セッションクッキーのパスを APPLICATION_ROOT に設定"""
        return self.APPLICATION_ROOT if self.APPLICATION_ROOT != '/' else None
    
    @property
    def SESSION_COOKIE_NAME(self):
        """セッションクッキー名をアプリケーション固有に設定"""
        if self.APPLICATION_ROOT and self.APPLICATION_ROOT != '/':
            # サブパスの場合、パス名を基にクッキー名を生成
            path_name = self.APPLICATION_ROOT.strip('/').replace('/', '_')
            return f'lft_{path_name}_session'
        return 'lft_session'
    
    # LibreChat設定
    LIBRECHAT_ROOT = os.environ.get('LIBRECHAT_ROOT') or '/path/to/librechat'
    LIBRECHAT_CONTAINER = os.environ.get('LIBRECHAT_CONTAINER') or 'LibreChat'
    LIBRECHAT_WORK_DIR = os.environ.get('LIBRECHAT_WORK_DIR') or '.'
    DOCKER_PATH = os.environ.get('DOCKER_PATH') or '/usr/bin/docker'