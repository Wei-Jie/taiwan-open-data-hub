"""
fetch_air_quality.py
抓取全台空氣品質 AQI 資料（環保署開放資料，免金鑰）
更新頻率：每 30 分鐘（由 GitHub Actions 觸發）
"""
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests

AQI_API_URL = "https://data.epa.gov.tw/api/v2/aqx_p_432?limit=1000&api_key=9be7b239-557b-4c10-9775-78cadfc555e9&format=json"
# 備用（無需 key 的舊版端點）
AQI_FALLBACK_URL = "https://opendata.epa.gov.tw/ws/Data/AQI/?$format=json"

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
    print("🔄 正在抓取 AQI 空氣品質資料...")
    try:
        resp = requests.get(AQI_FALLBACK_URL, timeout=30)
        resp.raise_for_status()
        raw_list = resp.json()
    except Exception as e:
        print(f"⚠️ 備用端點失敗：{e}，嘗試主端點...")
        resp = requests.get(AQI_API_URL, timeout=30)
        resp.raise_for_status()
        body = resp.json()
        raw_list = body.get("records", body)

    stations = []
    for item in raw_list:
        try:
            aqi_raw = item.get("AQI", "0") or "0"
            aqi_val = int(float(aqi_raw))
        except (ValueError, TypeError):
            aqi_val = 0

        level = get_aqi_level(aqi_val)
        stations.append({
            "site": item.get("SiteName", ""),
            "county": item.get("County", ""),
            "lat": float(item.get("Latitude") or 0),
            "lng": float(item.get("Longitude") or 0),
            "aqi": aqi_val,
            "status": item.get("Status", ""),
            "level": level["label"],
            "color": level["color"],
            "pm25": item.get("PM2.5", ""),
            "pm10": item.get("PM10", ""),
            "o3": item.get("O3", ""),
            "no2": item.get("NO2", ""),
            "publish_time": item.get("PublishTime", ""),
        })

    return {
        "updated_at": datetime.now(TW_TZ).isoformat(),
        "total_stations": len(stations),
        "stations": stations,
    }


def main():
    try:
        data = fetch_aqi()
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✅ AQI 資料寫入完成，共 {data['total_stations']} 測站")
    except Exception as e:
        print(f"❌ 抓取失敗：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
