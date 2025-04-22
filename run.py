from app import create_app
from app.models import db
from config import Config
from flask import Flask, redirect, url_for

app = create_app(Config)

# サブパスでのデプロイに対応するための設定
if app.config['APPLICATION_ROOT'] and app.config['APPLICATION_ROOT'] != '/':
    # アプリケーションルートがサブパスに設定されている場合
    from werkzeug.middleware.dispatcher import DispatcherMiddleware
    from werkzeug.wrappers import Response
    
    # ルートパスにダミーアプリケーションを配置
    def simple(env, resp):
        return Response(f'このアプリケーションは {app.config["APPLICATION_ROOT"]} でアクセスしてください')(env, resp)
    
    # DispatcherMiddlewareでアプリケーションをサブパスにマウント
    app.wsgi_app = DispatcherMiddleware(simple, {app.config['APPLICATION_ROOT']: app.wsgi_app})

@app.cli.command('create-db')
def create_db():
    """データベーステーブルを作成"""
    with app.app_context():
        db.create_all()
        print('データベーステーブルを作成しました')

@app.cli.command('create-super-user')
def create_super_user():
    """スーパーユーザーを作成"""
    from app.models.user import SuperUser
    import getpass
    
    email = input('メールアドレス: ')
    username = input('ユーザー名: ')
    password = getpass.getpass('パスワード: ')
    
    super_user = SuperUser(
        email=email,
        username=username
    )
    super_user.set_password(password)
    
    with app.app_context():
        db.session.add(super_user)
        db.session.commit()
    
    print(f'スーパーユーザー {username} を作成しました')

if __name__ == '__main__':
    app.run(debug=True)