import subprocess
import shlex
import json
import re

class LibreChatService:
    def __init__(self, librechat_root):
        self.librechat_root = librechat_root
    
    def create_user(self, email, username, name, password):
        """ユーザーを作成する"""
        # コマンドインジェクション対策のためにshlex.quoteを使用
        cmd = f"docker exec -it LibreChat-API /bin/sh -c \"cd .. && echo y | npm run create-user {shlex.quote(email)} {shlex.quote(username)} {shlex.quote(name)} {shlex.quote(password)} --email-verified=true\""
        return self._run_command(cmd)
    
    def delete_user(self, email):
        """ユーザーを削除する"""
        cmd = f"docker exec -it LibreChat-API /bin/sh -c \"cd .. && echo y | npm run delete-user {shlex.quote(email)}\""
        return self._run_command(cmd)
    
    def list_users(self):
        """ユーザー一覧を取得する"""
        cmd = "docker exec -it LibreChat-API /bin/sh -c \"cd .. && npm run list-users\""
        result = self._run_command(cmd)
        return self._parse_user_list(result.stdout) if result.returncode == 0 else []
    
    def _run_command(self, cmd):
        """コマンドを実行する"""
        return subprocess.run(cmd, shell=True, cwd=self.librechat_root, 
                             capture_output=True, text=True)
    
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