import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from .google_calendar import get_events, create_event

# FastAPIアプリケーションの作成
app = FastAPI(
    title="Google Calendar MCP Server",
    description="Model Context Protocol (MCP) server for Google Calendar API",
    version="1.0.0"
)

# MCPサーバーの設定ファイルのパス
MCP_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "mcp_config.json")

# MCPサーバーの設定を読み込む
def load_mcp_config():
    with open(MCP_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# イベント取得のリクエストモデル
class GetEventsRequest(BaseModel):
    calendar_id: Optional[str] = Field(default="primary", description="カレンダーID（デフォルトは'primary'）")
    max_results: Optional[int] = Field(default=10, description="取得する最大イベント数")
    start_date: Optional[str] = Field(default=None, description="イベント取得の開始日時（ISO形式）")
    end_date: Optional[str] = Field(default=None, description="イベント取得の終了日時（ISO形式）")
    query: Optional[str] = Field(default=None, description="検索クエリ")

# イベント作成のリクエストモデル
class CreateEventRequest(BaseModel):
    summary: str = Field(..., description="イベントのタイトル")
    start_time: str = Field(..., description="開始時間（ISO形式）")
    end_time: str = Field(..., description="終了時間（ISO形式）")
    description: Optional[str] = Field(default=None, description="イベントの説明")
    location: Optional[str] = Field(default=None, description="イベントの場所")
    calendar_id: Optional[str] = Field(default="primary", description="カレンダーID（デフォルトは'primary'）")

# MCPサーバーのメタデータを返すエンドポイント
@app.get("/")
def get_mcp_metadata():
    try:
        config = load_mcp_config()
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MCPサーバーの設定を読み込めませんでした: {str(e)}")

# MCPサーバーのツール情報を返すエンドポイント
@app.get("/tools")
def get_tools():
    try:
        # 設定ファイルから直接ツール情報を読み込む
        with open(MCP_CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
            return config.get("tools", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MCPサーバーのツール情報を読み込めませんでした: {str(e)}")

# MCPサーバーのリソース情報を返すエンドポイント
@app.get("/resources")
def get_resources():
    try:
        # 設定ファイルから直接リソース情報を読み込む
        with open(MCP_CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
            return config.get("resources", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MCPサーバーのリソース情報を読み込めませんでした: {str(e)}")

# イベント取得のエンドポイント
@app.post("/tools/get_events")
def tool_get_events(request: GetEventsRequest):
    try:
        # リクエストの内容をデバッグ出力
        print(f"tool_get_events - リクエスト: {request.dict()}")
        
        # 日時の変換
        time_min = None
        time_max = None
        
        if request.start_date:
            # ISO形式の日時文字列をdatetimeオブジェクトに変換
            print(f"tool_get_events - 元の開始日時: {request.start_date}")
            
            start_date = request.start_date
            if start_date.endswith('Z'):
                # 'Z'はUTCを表すので、'+00:00'に置き換える
                start_date = start_date[:-1] + '+00:00'
                print(f"tool_get_events - 変換後の開始日時文字列: {start_date}")
            
            time_min = datetime.fromisoformat(start_date)
            
            # デバッグ出力
            print(f"tool_get_events - 開始日時オブジェクト: {time_min}")
            print(f"tool_get_events - 開始日時タイムゾーン: {time_min.tzinfo}")
        
        if request.end_date:
            # ISO形式の日時文字列をdatetimeオブジェクトに変換
            print(f"tool_get_events - 元の終了日時: {request.end_date}")
            
            end_date = request.end_date
            if end_date.endswith('Z'):
                # 'Z'はUTCを表すので、'+00:00'に置き換える
                end_date = end_date[:-1] + '+00:00'
                print(f"tool_get_events - 変換後の終了日時文字列: {end_date}")
            
            time_max = datetime.fromisoformat(end_date)
            
            # デバッグ出力
            print(f"tool_get_events - 終了日時オブジェクト: {time_max}")
            print(f"tool_get_events - 終了日時タイムゾーン: {time_max.tzinfo}")
        
        # イベントを取得
        events = get_events(
            calendar_id=request.calendar_id,
            max_results=request.max_results,
            time_min=time_min,
            time_max=time_max,
            query=request.query
        )
        
        return {"events": events}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"イベントの取得に失敗しました: {str(e)}")

# イベント作成のエンドポイント
@app.post("/tools/create_event")
def tool_create_event(request: CreateEventRequest):
    try:
        # 日時の変換
        # ISO形式の日時文字列をdatetimeオブジェクトに変換
        start_time = datetime.fromisoformat(request.start_time.replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(request.end_time.replace('Z', '+00:00'))
        
        # デバッグ出力
        print(f"イベント作成 - 開始日時: {start_time}, タイムゾーン: {start_time.tzinfo}")
        print(f"イベント作成 - 終了日時: {end_time}, タイムゾーン: {end_time.tzinfo}")
        
        # イベントを作成
        event = create_event(
            summary=request.summary,
            start_time=start_time,
            end_time=end_time,
            description=request.description,
            location=request.location,
            calendar_id=request.calendar_id
        )
        
        return event
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"イベントの作成に失敗しました: {str(e)}")

# サーバー起動時の処理
@app.on_event("startup")
async def startup_event():
    print("Google Calendar MCP Server が起動しました")
    print(f"設定ファイル: {MCP_CONFIG_PATH}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
