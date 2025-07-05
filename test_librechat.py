#!/usr/bin/env python3
"""
LibreChatService インタラクティブテストスクリプト
ユーザー対話型でLibreChatの各機能をテストします
"""

import sys
import os
import json
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

# プロジェクトのルートディレクトリをパスに追加
sys.path.insert(0, '/Users/takahiro/Workspace/lft')

from app import create_app
from app.services.librechat import LibreChatService
from config import Config

def display_menu():
    """メニューを表示する"""
    print("\n=== LibreChat インタラクティブテストツール ===")
    print("1. ユーザー作成")
    print("2. ユーザー削除")
    print("3. ユーザー一覧取得")
    print("4. 設定情報表示")
    print("5. 終了")
    print("=" * 45)

def get_user_input():
    """ユーザーの選択を取得する"""
    while True:
        try:
            choice = input("選択してください (1-5): ").strip()
            if choice in ['1', '2', '3', '4', '5']:
                return int(choice)
            else:
                print("無効な選択です。1-5の数字を入力してください。")
        except KeyboardInterrupt:
            print("\n\n終了します。")
            sys.exit(0)

def test_create_user(service):
    """ユーザー作成テスト"""
    print("\n=== ユーザー作成テスト ===")
    
    try:
        email = input("Email: ").strip()
        if not email:
            print("Emailは必須です。")
            return
        
        username = input("Username: ").strip()
        if not username:
            print("Usernameは必須です。")
            return
        
        name = input("Name: ").strip()
        if not name:
            print("Nameは必須です。")
            return
        
        password = input("Password: ").strip()
        if not password:
            print("Passwordは必須です。")
            return
        
        print(f"\n実行内容:")
        print(f"  Email: {email}")
        print(f"  Username: {username}")
        print(f"  Name: {name}")
        print(f"  Password: {password}")
        
        confirm = input("\n実行しますか？ (y/N): ").strip().lower()
        if confirm != 'y':
            print("キャンセルしました。")
            return
        
        print("\n--- 実行開始 ---")
        result = service.create_user(email, username, name, password)
        
        print(f"\n--- 実行結果 ---")
        print(f"Return Code: {result.returncode}")
        if result.stdout:
            print(f"標準出力:\n{result.stdout}")
        if result.stderr:
            print(f"エラー出力:\n{result.stderr}")
        
        if result.returncode == 0:
            print("✅ ユーザー作成成功")
        else:
            print("❌ ユーザー作成失敗")
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")

def test_delete_user(service):
    """ユーザー削除テスト"""
    print("\n=== ユーザー削除テスト ===")
    
    try:
        email = input("削除するユーザーのEmail: ").strip()
        if not email:
            print("Emailは必須です。")
            return
        
        print(f"\n実行内容:")
        print(f"  削除対象Email: {email}")
        
        confirm = input("\n実行しますか？ (y/N): ").strip().lower()
        if confirm != 'y':
            print("キャンセルしました。")
            return
        
        print("\n--- 実行開始 ---")
        result = service.delete_user(email)
        
        print(f"\n--- 実行結果 ---")
        print(f"Return Code: {result.returncode}")
        if result.stdout:
            print(f"標準出力:\n{result.stdout}")
        if result.stderr:
            print(f"エラー出力:\n{result.stderr}")
        
        if result.returncode == 0:
            print("✅ ユーザー削除成功")
        else:
            print("❌ ユーザー削除失敗")
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")

def test_list_users(service):
    """ユーザー一覧取得テスト"""
    print("\n=== ユーザー一覧取得テスト ===")
    
    try:
        confirm = input("実行しますか？ (y/N): ").strip().lower()
        if confirm != 'y':
            print("キャンセルしました。")
            return
        
        print("\n--- 実行開始 ---")
        users = service.list_users()
        
        print(f"\n--- 実行結果 ---")
        print(f"取得したユーザー数: {len(users)}")
        
        if users:
            print("\nユーザー一覧:")
            for i, user in enumerate(users, 1):
                print(f"{i}. {user.get('email', 'N/A')} ({user.get('username', 'N/A')})")
                print(f"   Name: {user.get('name', 'N/A')}")
                print(f"   ID: {user.get('id', 'N/A')}")
                print(f"   Created: {user.get('created', 'N/A')}")
                print()
        else:
            print("ユーザーが見つかりませんでした。")
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")

def show_config(config):
    """設定情報を表示する"""
    print("\n=== 設定情報 ===")
    print(f"LibreChat Root: {config.LIBRECHAT_ROOT}")
    print(f"Container Name: {config.LIBRECHAT_CONTAINER}")
    print(f"Work Dir: {config.LIBRECHAT_WORK_DIR}")
    print(f"Docker Path: {config.DOCKER_PATH}")

def main():
    """メイン関数"""
    print("LibreChatService インタラクティブテストツール")
    print("=" * 50)
    
    # Flaskアプリケーションを作成
    app = create_app(Config)
    
    with app.app_context():
        # 設定を読み込み
        config = Config()
        
        # LibreChatServiceのインスタンスを作成
        service = LibreChatService(
            librechat_root=config.LIBRECHAT_ROOT,
            container_name=config.LIBRECHAT_CONTAINER,
            work_dir=config.LIBRECHAT_WORK_DIR,
            docker_path=config.DOCKER_PATH
        )
        
        while True:
            display_menu()
            choice = get_user_input()
            
            if choice == 1:
                test_create_user(service)
            elif choice == 2:
                test_delete_user(service)
            elif choice == 3:
                test_list_users(service)
            elif choice == 4:
                show_config(config)
            elif choice == 5:
                print("終了します。")
                break
            
            input("\nEnterキーを押して続行...")

if __name__ == "__main__":
    main()