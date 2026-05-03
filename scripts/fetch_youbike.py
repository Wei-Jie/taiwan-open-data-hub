"""
fetch_youbike.py
透過交通部 TDX API 抓取全台 YouBike 2.0 站點與即時資料
"""
import os
import json
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests

# TDX API 金鑰 (請在 GitHub Secrets 中設定)
CLIENT_ID = os.environ.get("TDX_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("TDX_CLIENT_SECRET", "")

# TDX 認證與資料端點
TOKEN_URL = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
# 全台 YouBike 站點基本資料
STATION_API = "https://tdx.transportdata.tw/api/basic/v2/Bike/Station/City"
# 全台 YouBike 即時剩餘資料
AVAILABILITY_API = "https://tdx.transportdata.tw/api/basic/v2/Bike/Availability/City"

# 輸出路徑
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "transport" / "youbike.json"
TW_TZ = timezone(timedelta(hours=8))


def get_tdx_token():
    """取得 TDX OAuth2 Access Token"""
    print("🔐 正在取得 TDX 認證 Token...")
    if not CLIENT_ID or not CLIENT_SECRET:
        print("⚠️ 警告: 未設定 TDX_CLIENT_ID 或 TDX_CLIENT_SECRET，將嘗試免金鑰抓取(可能失敗)...")
        return None

    data = {
        'content-type': 'application/x-www-form-urlencoded',
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    try:
        resp = requests.post(TOKEN_URL, data=data, timeout=20)
        resp.raise_for_status()
        return resp.json().get("access_token")
    except Exception as e:
        print(f"❌ 認證失敗: {e}")
        return None


def fetch_tdx_data(token):
    """抓取全台資料（TDX 的 'City' 留空代表全台或需循環，這裡採用最穩定的全台各縣市循環）"""
    headers = {"Accept-Encoding": "gzip"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    # TDX 支援的 YouBike 縣市清單
    cities = ["Taipei", "NewTaipei", "Taoyuan", "Taichung", "Tainan", "Kaohsiung", "Hsinchu", "Miaoli", "Pingtung"]
    
    all_stations = {}
    
    print(f"🔄 正在透過 TDX 抓取 {len(cities)} 縣市 YouBike 資料...")
    
    for city in cities:
        try:
            # 1. 抓取站點位置
            st_resp = requests.get(f"{STATION_API}/{city}?$format=JSON", headers=headers, timeout=20)
            # 2. 抓取即時狀態
            av_resp = requests.get(f"{AVAILABILITY_API}/{city}?$format=JSON", headers=headers, timeout=20)
            
            if st_resp.status_code == 200 and av_resp.status_code == 200:
                stations = st_resp.json()
                availability = {a["StationUID"]: a for a in av_resp.json()}
                
                for s in stations:
                    uid = s["StationUID"]
                    av = availability.get(uid, {})
                    
                    all_stations[uid] = {
                        "id": s.get("StationID", ""),
                        "name": s.get("StationName", {}).get("Zh_tw", "").replace("YouBike2.0_", ""),
                        "city": city,
                        "lat": s.get("StationPosition", {}).get("PositionLat", 0),
                        "lng": s.get("StationPosition", {}).get("PositionLon", 0),
                        "total": s.get("BikesCapacity", 0),
                        "available_bikes": av.get("AvailableRentBikes", 0),
                        "available_spaces": av.get("AvailableReturnBikes", 0),
                        "status": av.get("ServiceStatus", 1) # 1: 正常
                    }
                print(f"✅ {city} 載入完成")
            else:
                print(f"⚠️ {city} 資料擷取不完全 (Status: {st_resp.status_code})")
        except Exception as e:
            print(f"⚠️ {city} 抓取失敗: {e}")
            
    return list(all_stations.values())


def main():
    try:
        token = get_tdx_token()
        stations = fetch_tdx_data(token)
        
        if not stations:
            raise Exception("未抓取到任何站點資料。")

        data = {
            "updated_at": datetime.now(TW_TZ).isoformat(),
            "total_stations": len(stations),
            "stations": stations,
        }
            
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"🚀 全台 YouBike 資料寫入完成，共 {len(stations)} 站")
        
    except Exception as e:
        print(f"❌ 抓取失敗：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
