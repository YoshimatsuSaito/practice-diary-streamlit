# practice-diary-streamlit
- 練習記録用アプリ
- データベースを用いたアプリ作成の練習を兼ねる
- 完全に自分用の備忘リポジトリ

## 環境構築
- Bigqueryを使用するため、GCPのサービスアカウントを作成する
    - [gcpのservice_accountを作成する](https://cloud.google.com/docs/authentication/production?hl=ja)
    - jsonファイルをダウンロードし、pythonからのclientの作成に用いることで、外部からGCPのサービスが使えるようになる

## Bigqueryの基本・使い方
- [project name].[dataset name].[table name]という構造になる
- [それぞれを手動で操作することもできる](https://console.cloud.google.com/bigquery)
- `dataset`、`table`の作成、データのCRUDはpythonから行える
    - https://qiita.com/plumfield56/items/664d1a09edecb28880ca
    - https://www.rudderstack.com/guides/how-to-access-and-query-your-bigquery-data-using-python-and-r
    - https://qiita.com/Hyperion13fleet/items/0e00f4070f623dacf92b
- [streamlitとBigqueryとの接続に関するドキュメント](https://docs.streamlit.io/knowledge-base/tutorials/databases/bigquery)

## ログイン機能について
- [基本的には`streamlit_authenticator`を用いる](https://pypi.org/project/streamlit-authenticator/)
    - [前提とすべきフォーマットにあわせてアプリを構築する必要がある](https://stackoverflow.com/questions/73152424/streamlit-authenticate-init-got-multiple-values-for-argument-cookie-expir)
- [ただ、基本的な内容については自分で実装することも可能](https://zenn.dev/lapisuru/articles/3ae6dd82e36c29a27190)

## ディレクトリ構成
```
.
├── app.py
├── config.ini
├── service_account_info.json
├── modules
│   ├── authenticator_handler.py
│   ├── bq_handler.py
│   ├── practice_table_handler.py
│   ├── users_table_handler.py
│   └── utils.py
├── Pipfile
├── Pipfile.lock
├── README.md
├── scripts
│   ├── create_bq_dataset.py
│   └── create_first_user.py
├── service_account_info.json
└── views
    ├── add_practice.py
    ├── authenticate_user.py
    └── show_practice.py
```

## 各ファイルの概要
- `app.py`
    - アプリのホーム
    - 主に`modules/authenticator_handler`を用いて認証関連のウィジェットを配置する
    - ログインが成功した場合、`views/`以下の各ページの描画関数を呼び出す
- `config.ini`
    - Bigqueryのproject等の名前など、設定情報を載せる
    - gitには載せない
- `service_account_info.json`
    - GCPのサービスアカウント情報
    - gitには載せない
- `scripts/`
    - 基本的に一度きりの操作について格納する
    - `create_bq_dataset.py`
        - google cloudの該当プロジェクトについてdatasetを作成する
    - `create_first_user.py`
        - 便宜上、一人めのユーザを作成する
        - gitには載せない
- `views/`
    - `add_practice.py`
        - ログインされたユーザについて、各日の練習内容の入力を受け付け、練習記録テーブルに追加する
    - `show_practice.py`
        - ログインされたユーザについて、データベースの情報を表示する
- `modules/`
    - `utils.py`
        - 複数箇所で利用するような便利用関数を格納する
    - `bq_handler.py`
        - Bigqueryを直接操作するクラス
        - `practice_table_handler.py`や`users_table_handler.py`のような各テーブルについての処理を行うクラスから呼び出される
        - 特定のtable毎にインスタンスが作成されて機能する
    - `practice_table_handler.py`
        - 各ユーザが登録した練習記録を格納するテーブルを操作するクラス
        - 該当テーブル特有の処理をこのクラスが吸収する
        - 具体的な処理は`bq_handler.py`を用いて実行する
    - `users_table_handler.py`
        - 各ユーザのアカウント情報を格納するテーブルを操作するクラス
        - 該当テーブル特有の処理をこのクラスが吸収する
        - `streamlit_authenticator`が前提とするconfig形式とテーブルとの相互変換も担当する
        - 具体的な処理は`bq_handler.py`を用いて実行する
    - `authenticator_handler.py`
        - `authenticator_user.py`においてログイン、アカウント関連操作を行う際の`streamlit_authenticator`の各操作をまとめた便利クラス
        - `users_table_handler`を引数にとり、そのメソッドを用いて、データベースとのやりとりを行う
        - `streamlit_authenticator`が前提とするconfigの形式と、DBの形式との変換も行う


## 今回の作業中に調べた参考情報の備忘
### Cloud9のデバッガーの使い方
- [pythonpathにpipenv（仮想環境）のpathを加えればデバッグ実行が可能](https://predora005.hatenablog.com/entry/2020/09/25/190000)

### git secrets
- [AWSやGCPのアカウント情報を誤ってgithubにpushしないようにするためのツール](https://zenn.dev/kkk777/articles/8f55db1e9678f2)
- [AWSやGCPの出してはいけない情報についてのglobal設定](https://note.com/teitei_tk/n/ne1f2fa5a96bb)

### その他
- 普通にCRUDするだけならsqliteなどの方が良い
- 理想的にはflask sqlalchemyなどを用いて、どんなDBにも接続できる形にするべき
- トランザクションの管理などを明示的に実装する必要がある
- 列に対するユニーク制約などがかけられるDBが便利
- クラウドでやるならalloydbなどもありかも