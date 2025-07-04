import subprocess
import shlex
import json
import re
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
        # 詳細ログ記録用の辞書
        log_data = {
            'function': 'create_user',
            'email': email,
            'username': username,
            'name': name,
            'attempts': []
        }
        
        
        # すべての試行コマンドを用意
        commands = [
            # 通常の方法（work_dirを使用）
            f"{self.docker_path} exec -i {self.container_name} /bin/sh -c \"cd {self.work_dir} && echo y | npm run create-user {shlex.quote(email)} {shlex.quote(username)} {shlex.quote(name)} {shlex.quote(password)} --email-verified=true\"",
            
            # work_dirなし
            f"{self.docker_path} exec -i {self.container_name} /bin/sh -c \"echo y | npm run create-user {shlex.quote(email)} {shlex.quote(username)} {shlex.quote(name)} {shlex.quote(password)} --email-verified=true\"",
            
            # API直接アクセス
            f"{self.docker_path} exec -i {self.container_name} /bin/sh -c \"cd api && echo y | npm run create-user {shlex.quote(email)} {shlex.quote(username)} {shlex.quote(name)} {shlex.quote(password)} --email-verified=true\"",
            
            # ルートディレクトリからnpxを使用
            f"{self.docker_path} exec -i {self.container_name} /bin/sh -c \"echo y | npx --prefix=. create-user {shlex.quote(email)} {shlex.quote(username)} {shlex.quote(name)} {shlex.quote(password)} --email-verified=true\""
        ]
        
        # すべてのコマンドを順番に試す
        for i, cmd in enumerate(commands):
            try:
                print(f"DEBUG - 試行 {i+1}/{len(commands)}: {cmd}")
                result = self._run_command(cmd)
                
                # 詳細ログ
                attempt_log = {
                    'attempt_number': i+1,
                    'command': cmd,
                    'returncode': result.returncode,
                    'stdout_sample': result.stdout[:500] if result.stdout else '',
                    'stderr_sample': result.stderr[:500] if result.stderr else ''
                }
                log_data['attempts'].append(attempt_log)
                
                print(f"DEBUG - 試行 {i+1} 結果: {result.returncode}")
                if result.stdout:
                    print(f"DEBUG - 試行 {i+1} 標準出力: {result.stdout}")
                if result.stderr:
                    print(f"DEBUG - 試行 {i+1} エラー出力: {result.stderr}")
                
                # 成功したら終了
                if result.returncode == 0:
                    log_data['success'] = True
                    log_data['successful_attempt'] = i+1
                    print(f"DEBUG - ユーザー作成成功 (試行 {i+1}): {email}")
                    # システムログに成功を記録
                    SystemLog.log_action(
                        user_id=None,
                        user_type='system',
                        action='LibreChat ユーザー作成成功',
                        details=json.dumps(log_data, ensure_ascii=False)
                    )
                    print(f"LIBRECHAT_LOG: {json.dumps(log_data)}")
                    return result
            except Exception as e:
                print(f"DEBUG - 試行 {i+1} 例外: {str(e)}")
                log_data['attempts'].append({
                    'attempt_number': i+1,
                    'command': cmd,
                    'exception': str(e)
                })
                # システムログに例外を記録
                SystemLog.log_action(
                    user_id=None,
                    user_type='system',
                    action='LibreChat ユーザー作成エラー',
                    details=f"試行 {i+1}: {str(e)}"
                )
        
        # すべて失敗
        log_data['success'] = False
        print(f"DEBUG - すべての試行が失敗: {email}")
        # システムログに失敗を記録
        SystemLog.log_action(
            user_id=None,
            user_type='system',
            action='LibreChat ユーザー作成完全失敗',
            details=json.dumps(log_data, ensure_ascii=False)
        )
        print(f"LIBRECHAT_LOG: {json.dumps(log_data)}")
        
        # 最初のコマンドの結果を返す（互換性のため）
        return self._run_command(commands[0])
    
    def delete_user(self, email):
        """ユーザーを削除する"""
        # 詳細ログ記録用の辞書
        log_data = {
            'function': 'delete_user',
            'email': email,
            'attempts': []
        }
        
        # すべての試行コマンドを用意
        commands = [
            # 通常の方法（work_dirを使用）
            f"{self.docker_path} exec -i {self.container_name} /bin/sh -c \"cd {self.work_dir} && echo y | npm run delete-user {shlex.quote(email)}\"",
            
            # work_dirなし
            f"{self.docker_path} exec -i {self.container_name} /bin/sh -c \"echo y | npm run delete-user {shlex.quote(email)}\"",
            
            # API直接アクセス
            f"{self.docker_path} exec -i {self.container_name} /bin/sh -c \"cd api && echo y | npm run delete-user {shlex.quote(email)}\"",
            
            # ルートディレクトリからnpxを使用
            f"{self.docker_path} exec -i {self.container_name} /bin/sh -c \"echo y | npx --prefix=. delete-user {shlex.quote(email)}\""
        ]
        
        # すべてのコマンドを順番に試す
        for i, cmd in enumerate(commands):
            try:
                print(f"DEBUG - 削除試行 {i+1}/{len(commands)}: {cmd}")
                result = self._run_command(cmd)
                
                # 詳細ログ
                attempt_log = {
                    'attempt_number': i+1,
                    'command': cmd,
                    'returncode': result.returncode,
                    'stdout_sample': result.stdout[:500] if result.stdout else '',
                    'stderr_sample': result.stderr[:500] if result.stderr else ''
                }
                log_data['attempts'].append(attempt_log)
                
                print(f"DEBUG - 削除試行 {i+1} 結果: {result.returncode}")
                if result.stdout:
                    print(f"DEBUG - 削除試行 {i+1} 標準出力: {result.stdout}")
                if result.stderr:
                    print(f"DEBUG - 削除試行 {i+1} エラー出力: {result.stderr}")
                
                # 成功したら終了
                if result.returncode == 0:
                    log_data['success'] = True
                    log_data['successful_attempt'] = i+1
                    print(f"DEBUG - ユーザー削除成功 (試行 {i+1}): {email}")
                    # システムログに成功を記録
                    SystemLog.log_action(
                        user_id=None,
                        user_type='system',
                        action='LibreChat ユーザー削除成功',
                        details=json.dumps(log_data, ensure_ascii=False)
                    )
                    print(f"LIBRECHAT_LOG: {json.dumps(log_data)}")
                    return result
            except Exception as e:
                print(f"DEBUG - 削除試行 {i+1} 例外: {str(e)}")
                log_data['attempts'].append({
                    'attempt_number': i+1,
                    'command': cmd,
                    'exception': str(e)
                })
                # システムログに例外を記録
                SystemLog.log_action(
                    user_id=None,
                    user_type='system',
                    action='LibreChat ユーザー削除エラー',
                    details=f"試行 {i+1}: {str(e)}"
                )
        
        # すべて失敗
        log_data['success'] = False
        print(f"DEBUG - すべての削除試行が失敗: {email}")
        # システムログに失敗を記録
        SystemLog.log_action(
            user_id=None,
            user_type='system',
            action='LibreChat ユーザー削除完全失敗',
            details=json.dumps(log_data, ensure_ascii=False)
        )
        print(f"LIBRECHAT_LOG: {json.dumps(log_data)}")
        
        # 最初のコマンドの結果を返す（互換性のため）
        return self._run_command(commands[0])
    
    def list_users(self):
        """ユーザー一覧を取得する"""
        # 詳細ログ記録用の辞書
        log_data = {
            'function': 'list_users',
            'attempts': []
        }
        
        # すべての試行コマンドを用意
        commands = [
            # 通常の方法（work_dirを使用）
            f"{self.docker_path} exec -i {self.container_name} /bin/sh -c \"cd {self.work_dir} && npm run list-users\"",
            
            # work_dirなし
            f"{self.docker_path} exec -i {self.container_name} /bin/sh -c \"npm run list-users\"",
            
            # API直接アクセス
            f"{self.docker_path} exec -i {self.container_name} /bin/sh -c \"cd api && npm run list-users\"",
            
            # ルートディレクトリからnpxを使用
            f"{self.docker_path} exec -i {self.container_name} /bin/sh -c \"npx --prefix=. list-users\""
        ]
        
        # すべてのコマンドを順番に試す
        for i, cmd in enumerate(commands):
            try:
                print(f"DEBUG - 一覧試行 {i+1}/{len(commands)}: {cmd}")
                result = self._run_command(cmd)
                
                # 詳細ログ
                attempt_log = {
                    'attempt_number': i+1,
                    'command': cmd,
                    'returncode': result.returncode,
                    'stdout_sample': result.stdout[:500] if result.stdout else '',
                    'stderr_sample': result.stderr[:500] if result.stderr else ''
                }
                log_data['attempts'].append(attempt_log)
                
                print(f"DEBUG - 一覧試行 {i+1} 結果: {result.returncode}")
                if result.stdout:
                    print(f"DEBUG - 一覧試行 {i+1} 標準出力: {result.stdout}")
                if result.stderr:
                    print(f"DEBUG - 一覧試行 {i+1} エラー出力: {result.stderr}")
                
                # 成功したら終了
                if result.returncode == 0:
                    users = self._parse_user_list(result.stdout)
                    log_data['success'] = True
                    log_data['successful_attempt'] = i+1
                    log_data['users_count'] = len(users)
                    print(f"DEBUG - ユーザー一覧取得成功 (試行 {i+1}): {len(users)}件")
                    # システムログに成功を記録
                    SystemLog.log_action(
                        user_id=None,
                        user_type='system',
                        action='LibreChat ユーザー一覧取得成功',
                        details=json.dumps(log_data, ensure_ascii=False)
                    )
                    print(f"LIBRECHAT_LOG: {json.dumps(log_data)}")
                    return users
            except Exception as e:
                print(f"DEBUG - 一覧試行 {i+1} 例外: {str(e)}")
                log_data['attempts'].append({
                    'attempt_number': i+1,
                    'command': cmd,
                    'exception': str(e)
                })
                # システムログに例外を記録
                SystemLog.log_action(
                    user_id=None,
                    user_type='system',
                    action='LibreChat ユーザー一覧取得エラー',
                    details=f"試行 {i+1}: {str(e)}"
                )
        
        # すべて失敗
        log_data['success'] = False
        log_data['users_count'] = 0
        print(f"DEBUG - すべての一覧試行が失敗")
        # システムログに失敗を記録
        SystemLog.log_action(
            user_id=None,
            user_type='system',
            action='LibreChat ユーザー一覧取得完全失敗',
            details=json.dumps(log_data, ensure_ascii=False)
        )
        print(f"LIBRECHAT_LOG: {json.dumps(log_data)}")
        
        return []
    
    def _run_command(self, cmd):
        """コマンドを実行する"""
        print(f"DEBUG - 実行コマンド: {cmd}")
        print(f"DEBUG - 作業ディレクトリ: {self.librechat_root}")
        result = subprocess.run(cmd, shell=True, cwd=self.librechat_root, 
                              capture_output=True, text=True)
        print(f"DEBUG - 戻り値: {result.returncode}")
        if result.stdout:
            print(f"DEBUG - 標準出力: {result.stdout[:200]}...")
        if result.stderr:
            print(f"DEBUG - エラー出力: {result.stderr[:200]}...")
        return result
    
    def _parse_user_list(self, output):
        """コマンド出力からユーザー一覧を解析する"""
        users = []
        try:
            # 出力からJSON形式のデータを検出して解析
            # 実際の出力形式はLibreChatの実装に依存するため、
            # 必要に応じてこの部分は調整する必要があります
            json_match = re.search(r'\[(.*)\]', output, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                user_data = json.loads(json_str)
                for user in user_data:
                    users.append({
                        'email': user.get('email'),
                        'username': user.get('username'),
                        'name': user.get('name')
                    })
        except Exception as e:
            print(f"ユーザーリスト解析エラー: {e}")
        
        return users