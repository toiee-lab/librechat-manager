import subprocess
import shlex
import json
import re

class LibreChatService:
    def __init__(self, librechat_root, container_name="LibreChat", work_dir=".."):
        self.librechat_root = librechat_root
        self.container_name = container_name
        self.work_dir = work_dir
    
    def create_user(self, email, username, name, password):
        """ユーザーを作成する"""
        # コマンドインジェクション対策のためにshlex.quoteを使用
        command_parts = [
            "docker", "exec", "-i", self.container_name, "/bin/sh", "-c",
            f"cd {self.work_dir} && echo y | npm run create-user {shlex.quote(email)} {shlex.quote(username)} {shlex.quote(name)} {shlex.quote(password)} --email-verified=true"
        ]
        print(f"DEBUG - コマンド配列: {command_parts}")
        
        # 通常のシェルコマンド形式
        cmd = f"docker exec -i {self.container_name} /bin/sh -c \"cd {self.work_dir} && echo y | npm run create-user {shlex.quote(email)} {shlex.quote(username)} {shlex.quote(name)} {shlex.quote(password)} --email-verified=true\""
        
        # 本番環境とローカル環境の違いに対応するため、別の形式も試す
        alt_cmd = f"docker exec -i {self.container_name} /bin/sh -c \"echo y | npm run create-user {shlex.quote(email)} {shlex.quote(username)} {shlex.quote(name)} {shlex.quote(password)} --email-verified=true\""
        
        # 直接実行を試みる
        try:
            print(f"DEBUG - 直接実行試行: {' '.join(command_parts)}")
            direct_result = subprocess.run(command_parts, cwd=self.librechat_root, capture_output=True, text=True)
            print(f"DEBUG - 直接実行結果: {direct_result.returncode}")
            if direct_result.stdout:
                print(f"DEBUG - 直接実行標準出力: {direct_result.stdout[:200]}...")
            if direct_result.stderr:
                print(f"DEBUG - 直接実行エラー: {direct_result.stderr[:200]}...")
            
            # エラーがあれば代替コマンドを試す
            if direct_result.returncode != 0:
                print(f"DEBUG - 代替コマンド試行: {alt_cmd}")
                alt_result = self._run_command(alt_cmd)
                if alt_result.returncode == 0:
                    return alt_result
            
            return direct_result
        except Exception as e:
            print(f"DEBUG - 直接実行エラー例外: {str(e)}")
            # 失敗したら通常の方法にフォールバック
            return self._run_command(cmd)
    
    def delete_user(self, email):
        """ユーザーを削除する"""
        cmd = f"docker exec -i {self.container_name} /bin/sh -c \"cd {self.work_dir} && echo y | npm run delete-user {shlex.quote(email)}\""
        
        # 本番環境とローカル環境の違いに対応するため、まず標準のコマンドを試す
        result = self._run_command(cmd)
        
        # エラーがあれば代替コマンドを試す
        if result.returncode != 0:
            alt_cmd = f"docker exec -i {self.container_name} /bin/sh -c \"echo y | npm run delete-user {shlex.quote(email)}\""
            print(f"DEBUG - 代替削除コマンド試行: {alt_cmd}")
            alt_result = self._run_command(alt_cmd)
            if alt_result.returncode == 0:
                return alt_result
        
        return result
    
    def list_users(self):
        """ユーザー一覧を取得する"""
        cmd = f"docker exec -i {self.container_name} /bin/sh -c \"cd {self.work_dir} && npm run list-users\""
        result = self._run_command(cmd)
        
        # エラーがあれば代替コマンドを試す
        if result.returncode != 0:
            alt_cmd = f"docker exec -i {self.container_name} /bin/sh -c \"npm run list-users\""
            print(f"DEBUG - 代替一覧コマンド試行: {alt_cmd}")
            alt_result = self._run_command(alt_cmd)
            if alt_result.returncode == 0:
                return self._parse_user_list(alt_result.stdout)
        
        return self._parse_user_list(result.stdout) if result.returncode == 0 else []
    
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