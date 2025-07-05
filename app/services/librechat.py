import subprocess
import shlex
import json
import os
from typing import Dict, Any, List
from app.models.logs import SystemLog

class LibreChatService:
    def __init__(self, librechat_root, container_name="LibreChat", work_dir="..", docker_path="/usr/bin/docker"):
        self.librechat_root = librechat_root
        self.container_name = container_name
        self.work_dir = work_dir
        # dockerコマンドのフルパスを設定（環境によって異なる場合がある）
        self.docker_path = docker_path
    
    def create_user(self, email, username, name, password):
        """ユーザーを作成する"""
        cmd = f"{self.docker_path} exec -it {self.container_name} /bin/sh -c \"cd {self.work_dir} && echo y | npm run create-user {shlex.quote(email)} {shlex.quote(username)} {shlex.quote(name)} {shlex.quote(password)} --email-verified=true\""
        
        log_data: Dict[str, Any] = {
            'function': 'create_user',
            'email': email,
            'username': username,
            'name': name,
            'command': cmd
        }
        
        try:
            print(f"DEBUG - コマンド実行: {cmd}")
            result = self._run_command(cmd)
            
            log_data.update({
                'returncode': result.returncode,
                'stdout_sample': result.stdout[:500] if result.stdout else '',
                'stderr_sample': result.stderr[:500] if result.stderr else ''
            })
            
            print(f"DEBUG - 実行結果: {result.returncode}")
            if result.stdout:
                print(f"DEBUG - 標準出力: {result.stdout}")
            if result.stderr:
                print(f"DEBUG - エラー出力: {result.stderr}")
            
            if result.returncode == 0:
                log_data['success'] = True
                print(f"DEBUG - ユーザー作成成功: {email}")
                SystemLog.log_action(
                    user_id=None,
                    user_type='system',
                    action='LibreChat ユーザー作成成功',
                    details=json.dumps(log_data, ensure_ascii=False)
                )
            else:
                log_data['success'] = False
                print(f"DEBUG - ユーザー作成失敗: {email}")
                SystemLog.log_action(
                    user_id=None,
                    user_type='system',
                    action='LibreChat ユーザー作成失敗',
                    details=json.dumps(log_data, ensure_ascii=False)
                )
            
            print(f"LIBRECHAT_LOG: {json.dumps(log_data)}")
            return result
            
        except Exception as e:
            log_data['success'] = False
            log_data['exception'] = str(e)
            print(f"DEBUG - 例外発生: {str(e)}")
            SystemLog.log_action(
                user_id=None,
                user_type='system',
                action='LibreChat ユーザー作成エラー',
                details=json.dumps(log_data, ensure_ascii=False)
            )
            print(f"LIBRECHAT_LOG: {json.dumps(log_data)}")
            raise
    
    def delete_user(self, email):
        """ユーザーを削除する"""
        cmd = f"{self.docker_path} exec -it {self.container_name} /bin/sh -c \"cd {self.work_dir} && echo y | npm run delete-user {shlex.quote(email)}\""
        
        log_data: Dict[str, Any] = {
            'function': 'delete_user',
            'email': email,
            'command': cmd
        }
        
        try:
            print(f"DEBUG - コマンド実行: {cmd}")
            result = self._run_command(cmd)
            
            log_data.update({
                'returncode': result.returncode,
                'stdout_sample': result.stdout[:500] if result.stdout else '',
                'stderr_sample': result.stderr[:500] if result.stderr else ''
            })
            
            print(f"DEBUG - 実行結果: {result.returncode}")
            if result.stdout:
                print(f"DEBUG - 標準出力: {result.stdout}")
            if result.stderr:
                print(f"DEBUG - エラー出力: {result.stderr}")
            
            if result.returncode == 0:
                log_data['success'] = True
                print(f"DEBUG - ユーザー削除成功: {email}")
                SystemLog.log_action(
                    user_id=None,
                    user_type='system',
                    action='LibreChat ユーザー削除成功',
                    details=json.dumps(log_data, ensure_ascii=False)
                )
            else:
                log_data['success'] = False
                print(f"DEBUG - ユーザー削除失敗: {email}")
                SystemLog.log_action(
                    user_id=None,
                    user_type='system',
                    action='LibreChat ユーザー削除失敗',
                    details=json.dumps(log_data, ensure_ascii=False)
                )
            
            print(f"LIBRECHAT_LOG: {json.dumps(log_data)}")
            return result
            
        except Exception as e:
            log_data['success'] = False
            log_data['exception'] = str(e)
            print(f"DEBUG - 例外発生: {str(e)}")
            SystemLog.log_action(
                user_id=None,
                user_type='system',
                action='LibreChat ユーザー削除エラー',
                details=json.dumps(log_data, ensure_ascii=False)
            )
            print(f"LIBRECHAT_LOG: {json.dumps(log_data)}")
            raise
    
    def list_users(self):
        """ユーザー一覧を取得する"""
        cmd = f"{self.docker_path} exec -it {self.container_name} /bin/sh -c \"cd {self.work_dir} && npm run list-users\""
        
        log_data: Dict[str, Any] = {
            'function': 'list_users',
            'command': cmd
        }
        
        try:
            print(f"DEBUG - コマンド実行: {cmd}")
            result = self._run_command(cmd)
            
            log_data.update({
                'returncode': result.returncode,
                'stdout_sample': result.stdout[:500] if result.stdout else '',
                'stderr_sample': result.stderr[:500] if result.stderr else ''
            })
            
            print(f"DEBUG - 実行結果: {result.returncode}")
            if result.stdout:
                print(f"DEBUG - 標準出力: {result.stdout}")
            if result.stderr:
                print(f"DEBUG - エラー出力: {result.stderr}")
            
            if result.returncode == 0:
                users = self._parse_user_list(result.stdout)
                log_data['success'] = True
                log_data['users_count'] = len(users)
                print(f"DEBUG - ユーザー一覧取得成功: {len(users)}件")
                SystemLog.log_action(
                    user_id=None,
                    user_type='system',
                    action='LibreChat ユーザー一覧取得成功',
                    details=json.dumps(log_data, ensure_ascii=False)
                )
                print(f"LIBRECHAT_LOG: {json.dumps(log_data)}")
                return users
            else:
                log_data['success'] = False
                log_data['users_count'] = 0
                print(f"DEBUG - ユーザー一覧取得失敗")
                SystemLog.log_action(
                    user_id=None,
                    user_type='system',
                    action='LibreChat ユーザー一覧取得失敗',
                    details=json.dumps(log_data, ensure_ascii=False)
                )
                print(f"LIBRECHAT_LOG: {json.dumps(log_data)}")
                return []
            
        except Exception as e:
            log_data['success'] = False
            log_data['users_count'] = 0
            log_data['exception'] = str(e)
            print(f"DEBUG - 例外発生: {str(e)}")
            SystemLog.log_action(
                user_id=None,
                user_type='system',
                action='LibreChat ユーザー一覧取得エラー',
                details=json.dumps(log_data, ensure_ascii=False)
            )
            print(f"LIBRECHAT_LOG: {json.dumps(log_data)}")
            return []
    
    def _run_command(self, cmd):
        """コマンドを実行する"""
        print(f"DEBUG - 実行コマンド: {cmd}")
        print(f"DEBUG - 作業ディレクトリ: {self.librechat_root}")
        
        # 作業ディレクトリが存在しない場合はNoneを指定
        work_dir = self.librechat_root if os.path.exists(self.librechat_root) else None
        if work_dir is None:
            print(f"DEBUG - 作業ディレクトリが存在しないため、cwdを指定せずに実行")
        
        result = subprocess.run(cmd, shell=True, cwd=work_dir, 
                              capture_output=True, text=True)
        print(f"DEBUG - 戻り値: {result.returncode}")
        if result.stdout:
            print(f"DEBUG - 標準出力: {result.stdout[:200]}...")
        if result.stderr:
            print(f"DEBUG - エラー出力: {result.stderr[:200]}...")
        return result
    
    def _parse_user_list(self, output: str) -> List[Dict[str, Any]]:
        """コマンド出力からユーザー一覧を解析する"""
        users: List[Dict[str, Any]] = []
        try:
            # LibreChatの出力形式を解析
            lines = output.split('\n')
            current_user = {}
            
            for line in lines:
                line = line.strip()
                if line.startswith('ID: '):
                    # 新しいユーザーの開始
                    if current_user:
                        users.append(current_user)
                    current_user = {'id': line[4:]}
                elif line.startswith('Email: '):
                    current_user['email'] = line[7:]
                elif line.startswith('Username: '):
                    current_user['username'] = line[10:]
                elif line.startswith('Name: '):
                    current_user['name'] = line[6:]
                elif line.startswith('Provider: '):
                    current_user['provider'] = line[10:]
                elif line.startswith('Created: '):
                    current_user['created'] = line[9:]
            
            # 最後のユーザーを追加
            if current_user:
                users.append(current_user)
                
        except Exception as e:
            print(f"ユーザーリスト解析エラー: {e}")
        
        return users