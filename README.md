# Google Calendar MCP Server

Google カレンダー API を使用してイベントの取得・登録を行う Model Context Protocol (MCP) サーバーです。

## 機能

この MCP サーバーは以下の機能を提供します：

1. **Google カレンダー API を使用したイベントの取得**

   - カレンダー ID の指定
   - 取得するイベント数の制限
   - 期間の指定
   - 検索クエリの指定

2. **Google カレンダー API を使用したイベントの登録**
   - イベントのタイトル、開始時間、終了時間の指定
   - イベントの説明、場所の指定
   - カレンダー ID の指定

## 前提条件

- Docker
- Docker Compose
- Google Cloud Platform のプロジェクトとカレンダー API の有効化
- OAuth 2.0 クライアント ID の作成と`client_secret.json`の取得

## セットアップ

### 1. リポジトリのクローン

```bash
git clone <リポジトリURL>
cd google-calendar-mcp
```

### 2. Google Cloud Platform の設定

1. [Google Cloud Console](https://console.cloud.google.com/)にアクセスし、プロジェクトを作成または選択します。
2. [API ライブラリ](https://console.cloud.google.com/apis/library)から「Google Calendar API」を検索して有効化します。
3. [認証情報](https://console.cloud.google.com/apis/credentials)ページで「認証情報を作成」→「OAuth クライアント ID」を選択します。
4. アプリケーションの種類として「デスクトップアプリケーション」を選択し、名前を入力して「作成」をクリックします。
5. 作成された認証情報の「JSON をダウンロード」をクリックし、ダウンロードしたファイルを`client_secret.json`という名前でプロジェクトのルートディレクトリに配置します。

### 3. Docker コンテナのビルドと実行

```bash
docker compose up -d
```

初回実行時は、Google アカウントでの OAuth 認証が必要です。以下のコマンドでログを確認し、表示される URL にアクセスして認証を行ってください：

```bash
docker compose logs -f
```

認証が完了すると、`token.json`ファイルが生成され、以降の実行では自動的に認証が行われます。

## MCP サーバーの使用方法

### Cline での使用

Cline では、以下のように MCP サーバーを設定ファイルに追加することで使用できます：

```json
{
  "mcp_servers": [
    {
      "name": "google-calendar-mcp",
      "url": "http://localhost:8000"
    }
  ]
}
```

### Dify での使用

Dify を MCP クライアントとして使用するには、以下の手順に従ってください：

1. **Dify プロジェクトの設定**

   - Dify の管理画面にログインします
   - 使用したいアプリケーションを選択するか、新しいアプリケーションを作成します
   - 「設定」タブを選択し、「モデル」セクションに移動します

2. **MCP サーバーの追加**

   - 「MCP サーバー」セクションで「新規追加」をクリックします
   - 以下の情報を入力します：
     - 名前: `google-calendar-mcp`（任意の名前）
     - URL: `http://localhost:8000`（MCP サーバーの URL）
     - 認証トークン: 認証が必要な場合は入力（この MCP サーバーでは不要）
   - 「保存」をクリックします

3. **MCP ツールの有効化**

   - 「ツール」タブに移動します
   - 「MCP ツール」セクションで、追加した MCP サーバーから提供されるツールが表示されます
   - `get_events`と`create_event`ツールを有効にします

4. **プロンプト設定**

   - 「プロンプト」タブで、MCP ツールを使用するためのプロンプトを設定します
   - 例えば、以下のようなプロンプトを追加できます：
     ```
     あなたはGoogleカレンダーを管理するアシスタントです。
     ユーザーのカレンダーイベントの取得や作成を手伝ってください。
     ```

5. **アプリケーションの公開**

   - 設定が完了したら、アプリケーションを公開します

### イベント取得の例

#### Cline での例

```
<use_mcp_tool>
<server_name>google-calendar-mcp</server_name>
<tool_name>get_events</tool_name>
<arguments>
{
  "max_results": 5,
  "start_date": "2025-06-01T00:00:00Z",
  "end_date": "2025-06-30T23:59:59Z"
}
</arguments>
</use_mcp_tool>
```

#### Dify での例

Dify では、以下のようにツールを呼び出すことができます：

```
ツール: google-calendar-mcp.get_events
パラメータ:
{
  "max_results": 5,
  "start_date": "2025-06-01T00:00:00Z",
  "end_date": "2025-06-30T23:59:59Z"
}
```

### イベント作成の例

#### Cline での例

```
<use_mcp_tool>
<server_name>google-calendar-mcp</server_name>
<tool_name>create_event</tool_name>
<arguments>
{
  "summary": "ミーティング",
  "start_time": "2025-06-10T10:00:00+09:00",
  "end_time": "2025-06-10T11:00:00+09:00",
  "description": "プロジェクトの進捗確認",
  "location": "会議室A"
}
</arguments>
</use_mcp_tool>
```

#### Dify での例

```
ツール: google-calendar-mcp.create_event
パラメータ:
{
  "summary": "ミーティング",
  "start_time": "2025-06-10T10:00:00+09:00",
  "end_time": "2025-06-10T11:00:00+09:00",
  "description": "プロジェクトの進捗確認",
  "location": "会議室A"
}
```

## API エンドポイント

MCP サーバーは以下のエンドポイントを提供します：

- `GET /` - MCP サーバーのメタデータを取得
- `GET /tools` - 利用可能なツールの一覧を取得
- `GET /resources` - 利用可能なリソースの一覧を取得
- `POST /tools/get_events` - カレンダーイベントを取得
- `POST /tools/create_event` - カレンダーイベントを作成

## トラブルシューティング

### 認証エラー

認証に問題がある場合は、以下の手順を試してください：

1. `token.json`ファイルを削除
2. Docker コンテナを再起動（`docker compose restart`）
3. ログに表示される URL で再認証

### API リクエストの制限

Google Calendar API には[利用制限](https://developers.google.com/calendar/api/guides/quota)があります。制限に達した場合は、しばらく待ってから再試行してください。

### Dify との接続問題

Dify から MCP サーバーに接続できない場合は、以下を確認してください：

1. **ネットワーク接続**

   - MCP サーバーが Dify からアクセス可能なネットワーク上にあることを確認します
   - ローカルで実行している場合は、Dify と MCP サーバーが同じネットワーク上にあるか、適切なポート転送が設定されていることを確認します

2. **CORS 設定**

   - Dify からのリクエストが CORS (Cross-Origin Resource Sharing) によってブロックされていないことを確認します
   - 必要に応じて、MCP サーバーの CORS 設定を調整します

3. **URL の確認**

   - MCP サーバーの URL が正しく設定されていることを確認します
   - プロトコル（http/https）、ホスト名、ポート番号が正確であることを確認します

4. **サーバーの状態確認**
   - MCP サーバーが正常に動作していることを確認します：
     ```bash
     curl http://localhost:8000
     ```
   - 正常な応答が返ってくることを確認します

## ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。
