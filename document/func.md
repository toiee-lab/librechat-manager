# 3. 機能仕様

## 3.1 スーパーユーザー機能の詳細

### 講師アカウント管理
講師アカウントの作成・編集・削除を行う機能を提供します。

#### ユーザーストーリー
- スーパーユーザーとして、新しい講師アカウントを作成したい。それは新たに授業を担当する講師を追加するためである。
- スーパーユーザーとして、既存の講師情報を編集したい。それは講師の管理情報や権限を適切に更新するためである。
- スーパーユーザーとして、不要になった講師アカウントを削除したい。それは離職した講師のアクセス権を剥奪するためである。

#### 入出力例
- 入力: 講師の基本情報（メールアドレス、氏名、初期パスワード、プレフィックス）
- 出力: 作成された講師アカウント情報、成功/失敗メッセージ

### 講師設定管理
講師ごとの設定（最大ユーザー作成数）を管理します。プレフィックスは作成時のみ設定可能で、後から修正はできません。

#### ユーザーストーリー
- スーパーユーザーとして、講師ごとの最大ユーザー数を設定したい。それはシステムリソースを適切に配分するためである。

#### 入出力例
- 入力: 講師ID、最大ユーザー数（例: 20）
- 出力: 更新された設定情報、成功/失敗メッセージ

### 活動ログ監視
講師の活動ログを閲覧・監視する機能を提供します。

#### ユーザーストーリー
- スーパーユーザーとして、講師の活動ログを閲覧したい。それはシステム使用状況を把握し、必要に応じてサポートするためである。

#### 入出力例
- 入力: 検索条件（日付範囲、講師ID、アクション種別）
- 出力: 条件に合致する活動ログの一覧（日時、講師名、IPアドレス、実行アクション、詳細）

## 3.2 講師向け機能の詳細

### 生徒アカウントの一括作成
講師が担当する生徒のアカウントを一括で作成する機能を提供します。

#### ユーザーストーリー
- 講師として、担当するクラスの生徒アカウントを一括作成したい。それは授業準備を効率的に行うためである。

#### 入出力例
- 入力: 作成数（1〜20）
- 出力: 
  * 作成された生徒アカウント一覧（メールアドレス、パスワード）
  * 作成に成功したアカウント数
  * 生成されたアカウント情報（メールアドレス、パスワードのみ）をCSVでダウンロード可能
  * パスワードは英数半角8文字のランダム文字列を自動生成

### 生徒アカウントの一括リセット
既存の生徒アカウントを全て削除し、新たに作成し直す機能を提供します。

#### ユーザーストーリー
- 講師として、過去の授業で使用した生徒アカウントをリセットしたい。それは次の授業で新鮮な状態で利用するためである。

#### 入出力例
- 入力: リセット実行の確認
- 出力: 
  * リセット完了メッセージ
  * 新しいアカウント情報一覧（メールアドレス、パスワード）
  * 新しく生成されたパスワード（英数半角8文字のランダム文字列）

### 生徒アカウント一覧表示
講師が管理している生徒アカウントの一覧を表示する機能を提供します。

#### ユーザーストーリー
- 講師として、自分が管理する生徒アカウントの一覧を確認したい。それは現在の管理状況を把握するためである。

#### 入出力例
- 入力: なし
- 出力: 生徒アカウント一覧（メールアドレス、ユーザー名、作成日時）、総数

## 3.3 システム管理機能の詳細

### ユーザー数の上限管理
講師ごとに作成可能な生徒アカウント数の上限を管理する機能を提供します。

#### ユーザーストーリー
- スーパーユーザーとして、講師ごとの生徒アカウント作成上限を設定・変更したい。それはシステムリソースを適切に配分し、必要に応じて柔軟に調整するためである。

#### 入出力例
- 入力: 講師ID、新しい上限値
- 出力: 更新完了メッセージ、現在の設定一覧

### システム操作ログの管理
システム全体の操作ログを記録・閲覧する機能を提供します。

#### ユーザーストーリー
- スーパーユーザーとして、システム全体の操作ログを閲覧したい。それは不正アクセスの検知やトラブルシューティングのためである。

#### 入出力例
- 入力: 検索条件（日付範囲、ユーザー種別、アクション種別）
- 出力: 条件に合致する操作ログの一覧（日時、ユーザーID、ユーザー種別、IPアドレス、アクション、詳細）

## 3.4 認証・アクセス制御機能の詳細

### ユーザー認証
システムへのログイン・ログアウト機能を提供します。

#### ユーザーストーリー
- ユーザーとして、安全にシステムにログインしたい。それは自分のアカウントでの操作を行うためである。
- ユーザーとして、使用後に確実にログアウトしたい。それはセキュリティを確保するためである。

#### 入出力例
- 入力: メールアドレス、パスワード
- 出力: 認証結果（成功/失敗）、ユーザーロールに応じたダッシュボードへのリダイレクト

### ロールベースアクセス制御
ユーザーのロール（スーパーユーザー/講師）に基づき、アクセス可能な機能を制御します。

#### ユーザーストーリー
- スーパーユーザーとして、システム全体の管理機能にアクセスしたい。それはシステム全体を適切に運用管理するためである。
- 講師として、自分が担当する生徒アカウントのみを管理したい。それは自分の授業の準備と運営に集中するためである。

#### 入出力例
- 入力: ユーザーの認証情報とロール
- 出力: アクセス可能な機能メニューの表示、権限がない機能へのアクセス時のエラーメッセージ