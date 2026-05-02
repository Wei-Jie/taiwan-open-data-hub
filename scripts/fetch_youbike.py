"""
fetch_youbike.py
抓取 YouBike 全台站點即時資料（YouBike 官方公開 API，免金鑰）
更新頻率：每 30 分鐘（由 GitHub Actions 觸發）
"""
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests

# YouBike 官方 API - 全台所有城市一次回傳
YOUBIKE_API_URL = "https://apis.youbike.com.tw/api/front/station/list?lang=tw&type=2"
# 備用：台北市公開資料
YOUBIKE_FALLBACK_URL = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; TaiwanOpenDataHub/1.0)",
    "Accept": "application/json",
}

OUTPUT_PATH = Path(__file__).parent.parent / "data" / "transport" / "youbike.json"

# 台灣時區 UTC+8
TW_TZ = timezone(timedelta(hours=8))


def fetch_youbike() -> dict:
    """抓取 YouBike 全台站點資料並整理格式"""
    print("🔄 正在抓取 YouBike 全台資料...")

    stations_raw = []
    try:
        response = requests.get(YOUBIKE_API_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
        raw = response.json()
        stations_raw = raw.get("retVal", raw) if isinstance(raw, dict) else raw
    except Exception as e:
        print(f"⚠️ 主端點失敗（{e}），使用台北備用端點...")
        response = requests.get(YOUBIKE_FALLBACK_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
        raw = response.json()
        # 台北備用格式不同，key 是站號字串
        if isinstance(raw, dict):
            stations_raw = list(raw.values())
        else:
            stations_raw = raw

    # 整理欄位，僅保留前端需要的欄位
    result = []
    for s in stations_raw:
        result.append({
            "id": s.get("station_no", ""),
            "name": s.get("station_name", {}).get("zh_tw", s.get("name_tw", "")),
            "city": s.get("city_tw", s.get("city", "")),
            "lat": float(s.get("latitude", 0) or 0),
            "lng": float(s.get("longitude", 0) or 0),
            "total": int(s.get("total", 0) or 0),
            "available_bikes": int(s.get("available_rent_bikes", 0) or 0),
            "available_spaces": int(s.get("available_return_bikes", 0) or 0),
        })

    return {
        "updated_at": datetime.now(TW_TZ).isoformat(),
        "total_stations": len(result),
        "stations": result,
    }


def main():
    try:
        data = fetch_youbike()
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✅ YouBike 資料寫入完成，共 {data['total_stations']} 站")
    except Exception as e:
        print(f"❌ 抓取失敗：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
