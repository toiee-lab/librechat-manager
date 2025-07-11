# LibreChatユーザー管理システム (LFT)

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
- **フロントエンド**: TailwindCSS、Jinja2テンプレート
- **データベース**: SQLite3（SQLAlchemy ORM）
- **認証**: Flask-Login
- **セキュリティ**: Flask-WTF（CSRF保護）

## インストール手順

### 前提条件
- Python 3.9以上
- LibreChatがインストールされた同一サーバー
- Nginx（リバースプロキシ用）

### セットアップ
1. リポジトリをクローン
   ```
   git clone https://github.com/toiee-lab/librechat-manager.git lft
   cd lft
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
   `.env`ファイルを編集し、以下の設定を行います：
   ```
   SECRET_KEY=安全な乱数値を設定
   LIBRECHAT_ROOT=/path/to/librechat  # LibreChatのルートディレクトリ
   LIBRECHAT_CONTAINER=LibreChat      # コンテナ名（デフォルトはLibreChat）
   LIBRECHAT_WORK_DIR=.               # docker-compose.ymlがある作業ディレクトリ
   DOCKER_PATH=/usr/bin/docker        # dockerコマンドの絶対パス（which dockerで確認）
   ```

4. データベースを初期化
   ```
   flask create-db
   ```

5. スーパーユーザーを作成
   ```
   flask create-super-user
   ```

## 本番環境へのデプロイ

### 環境設定ファイルの作成

少し複雑。

```
cp .env.example .env
```
`.env`ファイルを編集し、以下の設定を行います：
```
SECRET_KEY=安全な乱数値を設定
APPLICATION_ROOT=/
LIBRECHAT_ROOT=/path/to/librechat  # LibreChatのルートディレクトリ
LIBRECHAT_CONTAINER=LibreChat-API      # コンテナ名（docker ps で確認する）
LIBRECHAT_WORK_DIR=..               # create-user が含まれる package.jsonがある場所
DOCKER_PATH=/usr/bin/docker        # dockerコマンドの絶対パス（which dockerで確認）
```


### Gunicornの設定

必要なパッケージをインストール
```
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

テストで立ち上げる

```
gunicorn -w 4 -b 127.0.0.1:8000 "run:app"
```

### systemdサービスとして設定

```
sudo nano /etc/systemd/system/lft.service
```

以下を参考に記載する

```
[Unit]
Description=LibreChat User Manager
After=network.target

[Service]
User=yourusername
WorkingDirectory=/path/to/lft
Environment="PATH=/path/to/lft/venv/bin:/usr/bin:/bin"
ExecStart=/path/to/lft/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 "run:app"
Restart=always

[Install]
WantedBy=multi-user.target
```

編集が完了したら、以下のコマンドでシステムにサービスを認識させる

```
sudo systemctl daemon-reload
```

サービスを有効化して自動起動するように設定します。
```
sudo systemctl enable lft.service
```

サービスの起動
```
sudo systemctl start lft.service
```

サービスの状態を確認

```
sudo systemctl status lft.service
```



### Nginxリバースプロキシ設定

LibreChatと同じサーバーで運用する場合のNginx設定例：

```
server {
    listen 80;
    server_name your-domain.com;

    # LFT (LibreChatユーザー管理システム)へのプロキシ設定
   location / {
      proxy_pass http://localhost:8000/;
      proxy_http_version 1.1;
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection 'upgrade';
      proxy_set_header Host $host;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
      proxy_cache_bypass $http_upgrade;
   }

    # LibreChatへのプロキシ設定
    location / {
        proxy_pass http://localhost:3080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

SSL設定を追加する場合：
```
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # 以下、上記と同じproxy_pass設定
    ...
}
```

### アップデート

```
git pull
source venv/bin/activate
pip install --upgrade -r requirements.txt

sudo systemctl restart lft
```

### ログの見方

```
sudo journalctl -u lft
```

アプリケーション固有のログ:

アプリケーションのルートディレクトリやログディレクトリ内のファイル。
以下のコマンドを実行すると、ログの場所がわかるかもしれません：

- Systemdサービスのログを確認
  sudo journalctl -u gunicorn

- プロセスのstdoutとstderrを追跡
```
ps aux | grep gunicorn
sudo tail -f /proc/<プロセスID>/fd/1  # 標準出力
sudo tail -f /proc/<プロセスID>/fd/2  # 標準エラー
```

- アプリディレクトリでログファイルを検索

```
find /path/to/your/app -name "*.log"
```

### LibreChatユーザー作成のトラブルシューティング

LibreChatユーザーが作成されない場合は、以下の2つの設定を確認してください：

1. **dockerコマンドへのパス**：
   - `.env`ファイルの`DOCKER_PATH`に正しいdockerの実行パスが設定されているか確認
   - `which docker`コマンドでdockerコマンドのフルパスを確認できます

2. **systemdサービス設定のPATH**：
   - `/etc/systemd/system/lft.service`の`Environment="PATH=..."`に`/usr/bin`や`/usr/local/bin`（dockerのインストール場所）が含まれているか確認

詳細なデバッグログには"LIBRECHAT_LOG:"で始まる行があり、JSONフォーマットで詳細な診断情報が記録されています。
このログを確認することで、どのコマンドが試行され、どのようなエラーが発生したかを特定できます。



## 使用方法

1. スーパーユーザーでログイン（/admin/login）
2. 講師アカウントを作成（プレフィックスを設定）
3. 講師アカウントでログイン（/login）し、生徒アカウントを作成
4. 必要に応じて生徒アカウントをリセット

## ライセンス

MITライセンスの下で公開されています。詳細はLICENSEファイルを参照してください。