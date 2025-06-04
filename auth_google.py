import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# 認証に必要なスコープ
SCOPES = ['https://www.googleapis.com/auth/calendar']

# トークンファイルのパス
TOKEN_FILE = 'token.json'
# クライアントシークレットファイルのパス
CLIENT_SECRET_FILE = 'client_secret.json'

def get_credentials():
    """GoogleカレンダーAPIの認証情報を取得する"""
    creds = None
    
    # トークンファイルが存在する場合は読み込む
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as token:
            creds = Credentials.from_authorized_user_info(json.load(token), SCOPES)
    
    # 認証情報が無効または存在しない場合は新たに取得
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # トークンを保存
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return creds

if __name__ == '__main__':
    print("GoogleカレンダーAPIの認証を開始します...")
    creds = get_credentials()
    print(f"認証が完了しました。トークンが {TOKEN_FILE} に保存されました。")
