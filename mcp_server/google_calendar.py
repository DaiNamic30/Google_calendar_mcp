import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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
            # ブラウザを開かずに認証URLを表示する
            auth_url, _ = flow.authorization_url(prompt='consent')
            print(f"\n\n認証URLにアクセスして認証を行ってください: {auth_url}\n\n")
            print("認証コードを入力してください:")
            code = input()
            creds = flow.fetch_token(code=code)
        
        # トークンを保存
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return creds

def get_calendar_service():
    """GoogleカレンダーAPIのサービスを取得する"""
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)
    return service

def get_events(
    calendar_id: str = 'primary',
    max_results: int = 10,
    time_min: Optional[datetime] = None,
    time_max: Optional[datetime] = None,
    query: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Googleカレンダーからイベントを取得する
    
    Args:
        calendar_id: カレンダーID（デフォルトは'primary'）
        max_results: 取得する最大イベント数
        time_min: イベント取得の開始時間
        time_max: イベント取得の終了時間
        query: 検索クエリ
        
    Returns:
        イベントのリスト
    """
    try:
        service = get_calendar_service()
        
        # デフォルトの時間範囲を設定（現在から1週間）
        if time_min is None:
            time_min = datetime.utcnow()
        if time_max is None:
            time_max = time_min + timedelta(days=7)
            
        # 時間をRFC3339形式に変換
        # RFC3339形式では、UTCの場合は'Z'、それ以外のタイムゾーンの場合は'+HH:MM'または'-HH:MM'を使用
        if time_min.tzinfo is not None:
            # タイムゾーン情報がある場合
            if time_min.tzinfo.utcoffset(time_min).total_seconds() == 0:
                # UTCの場合は'Z'を使用
                time_min_str = time_min.strftime('%Y-%m-%dT%H:%M:%SZ')
            else:
                # UTCでない場合はisoformat()を使用（'+HH:MM'形式）
                time_min_str = time_min.isoformat()
        else:
            # タイムゾーン情報がない場合はUTC（Z）として扱う
            time_min_str = time_min.strftime('%Y-%m-%dT%H:%M:%SZ')
            
        if time_max.tzinfo is not None:
            # タイムゾーン情報がある場合
            if time_max.tzinfo.utcoffset(time_max).total_seconds() == 0:
                # UTCの場合は'Z'を使用
                time_max_str = time_max.strftime('%Y-%m-%dT%H:%M:%SZ')
            else:
                # UTCでない場合はisoformat()を使用（'+HH:MM'形式）
                time_max_str = time_max.isoformat()
        else:
            # タイムゾーン情報がない場合はUTC（Z）として扱う
            time_max_str = time_max.strftime('%Y-%m-%dT%H:%M:%SZ')
            
        # デバッグ出力
        print(f"get_events - time_min: {time_min}, time_min_str: {time_min_str}")
        print(f"get_events - time_max: {time_max}, time_max_str: {time_max_str}")
        
        # イベント取得のパラメータ
        params = {
            'calendarId': calendar_id,
            'timeMin': time_min_str,
            'timeMax': time_max_str,
            'maxResults': max_results,
            'singleEvents': True,
            'orderBy': 'startTime'
        }
        
        # パラメータをデバッグ出力
        print(f"get_events - パラメータ: {params}")
        
        # 検索クエリがある場合は追加
        if query:
            params['q'] = query
            
        # イベントを取得
        events_result = service.events().list(**params).execute()
        events = events_result.get('items', [])
        
        return events
        
    except HttpError as error:
        print(f'エラーが発生しました: {error}')
        return []

def create_event(
    summary: str,
    start_time: datetime,
    end_time: datetime,
    description: Optional[str] = None,
    location: Optional[str] = None,
    calendar_id: str = 'primary'
) -> Dict[str, Any]:
    """
    Googleカレンダーにイベントを作成する
    
    Args:
        summary: イベントのタイトル
        start_time: 開始時間
        end_time: 終了時間
        description: イベントの説明
        location: イベントの場所
        calendar_id: カレンダーID（デフォルトは'primary'）
        
    Returns:
        作成されたイベントの情報
    """
    try:
        service = get_calendar_service()
        
        # イベントの詳細を設定
        event = {
            'summary': summary,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'Asia/Tokyo',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'Asia/Tokyo',
            }
        }
        
        # 説明がある場合は追加
        if description:
            event['description'] = description
            
        # 場所がある場合は追加
        if location:
            event['location'] = location
            
        # イベントを作成
        created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
        
        return created_event
        
    except HttpError as error:
        print(f'エラーが発生しました: {error}')
        return {}
