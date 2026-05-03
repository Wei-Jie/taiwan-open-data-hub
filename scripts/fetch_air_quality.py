"""
fetch_air_quality.py
抓取全台空氣品質 AQI 資料（環境部開放資料）
"""
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import os
import requests

# 環境部新版 API v2
# 請至 https://data.moenv.gov.tw/ 申請個人 API Key
# 並將其設定為 GitHub Secrets 中的 MOENV_API_KEY
API_KEY = os.environ.get("MOENV_API_KEY") 
if not API_KEY:
    print("❌ 錯誤: 未偵測到環境變數 MOENV_API_KEY。")
    print("💡 提示: 請在 GitHub Secrets 中設定此變數，或在本地環境設定。")
    sys.exit(1)

AQI_API_URL = f"https://data.moenv.gov.tw/api/v2/aqx_p_432?limit=1000&api_key={API_KEY}&format=json"

OUTPUT_PATH = Path(__file__).parent.parent / "data" / "transport" / "air_quality.json"
TW_TZ = timezone(timedelta(hours=8))

# AQI 等級對應
AQI_LEVELS = [
    (50,  "良好",     "green"),
    (100, "普通",     "yellow"),
    (150, "對敏感族群不健康", "orange"),
    (200, "不健康",   "red"),
    (300, "非常不健康", "purple"),
    (999, "危害",     "maroon"),
]


def get_aqi_level(aqi_val: int) -> dict:
    """根據 AQI 數值回傳等級與顏色"""
    for threshold, label, color in AQI_LEVELS:
        if aqi_val <= threshold:
            return {"label": label, "color": color}
    return {"label": "危害", "color": "maroon"}


def fetch_aqi() -> dict:
    """抓取 AQI 資料"""
    print("🔄 正在抓取環境部 AQI 空氣品質資料...")
    resp = requests.get(AQI_API_URL, timeout=30)
    
    if resp.status_code != 200:
        raise Exception(f"API 回傳錯誤代碼: {resp.status_code}")

    try:
        body = resp.json()
    except json.JSONDecodeError:
        content_snippet = resp.text[:100].replace('\n', ' ')
        raise Exception(f"無法解析 JSON 資料。API 回傳內容: {content_snippet}")
    
    # 彈性處理回傳格式：可能是 List，也可能是帶有 records 的 Dict
    if isinstance(body, list):
        raw_list = body
    elif isinstance(body, dict):
        raw_list = body.get("records", [])
    else:
        raise Exception(f"未知的 API 回傳格式: {type(body)}")

    if not raw_list:
        content_snippet = str(body)[:100]
        raise Exception(f"抓取到的資料列表為空。API 回傳內容: {content_snippet}")

    stations = []
    for item in raw_list:
        try:
            aqi_raw = item.get("aqi", "0") or "0"
            aqi_val = int(float(aqi_raw))
        except (ValueError, TypeError):
            aqi_val = 0

        level = get_aqi_level(aqi_val)
        stations.append({
            "site": item.get("sitename", ""),
            "county": item.get("county", ""),
            "lat": float(item.get("latitude") or 0),
            "lng": float(item.get("longitude") or 0),
            "aqi": aqi_val,
            "status": item.get("status", ""),
            "level": level["label"],
            "color": level["color"],
            "pm25": item.get("pm2.5", ""),
            "pm10": item.get("pm10", ""),
            "o3": item.get("o3", ""),
            "no2": item.get("no2", ""),
            "publish_time": item.get("publishtime", ""),
        })

    return {
        "updated_at": datetime.now(TW_TZ).isoformat(),
        "total_stations": len(stations),
        "stations": stations,
    }


def main():
    try:
        data = fetch_aqi()
        if not data["stations"]:
            raise Exception("抓取到的測站資料為空。")
            
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✅ AQI 資料寫入完成，共 {data['total_stations']} 測站")
    except Exception as e:
        print(f"❌ 抓取失敗：{e}", file=sys.stderr)
        # 如果是 API Key 問題，提醒使用者
        if "API KEY" in str(e) or "解析 JSON" in str(e):
            print("\n💡 提示：請檢查 scripts/fetch_air_quality.py 中的 API_KEY 是否有效。")
            print("您可以到 https://data.moenv.gov.tw/ 申請免費的 API Key。")
        sys.exit(1)


if __name__ == "__main__":
    main()
