"""
fetch_youbike.py
抓取全台主要縣市 YouBike 2.0 站點資料（整合多縣市政府開放資料）
"""
import json
import sys
import concurrent.futures
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests

# 縣市開放資料來源清單 (YouBike 2.0)
CITY_SOURCES = [
    {"city": "台北市", "url": "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"},
    {"city": "新北市", "url": "https://data.ntpc.gov.tw/api/datasets/01216db9-04f1-4433-a359-885f13f3500c/json?size=2000"},
    {"city": "桃園市", "url": "https://data.tycg.gov.tw/api/v1/rest/datastore/a1b4714b-3b75-4bc8-a789-f35551f33f74?format=json"},
    {"city": "台中市", "url": "https://datacenter.taichung.gov.tw/swagger/OpenData/86dfad5c-540c-4479-bb7d-d72961d0349d"},
    {"city": "台南市", "url": "https://tbike-data.tainan.gov.tw/Service/StationStatus/Json"},
    {"city": "高雄市", "url": "https://api.kcg.gov.tw/api/service/Get/b4dd9c40-9027-4127-868c-05183cbb1488"},
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; TaiwanOpenDataHub/1.0)",
}

OUTPUT_PATH = Path(__file__).parent.parent / "data" / "transport" / "youbike.json"
TW_TZ = timezone(timedelta(hours=8))


def fetch_city_data(city_info: dict) -> list:
    """抓取單一縣市的資料並標準化"""
    city = city_info["city"]
    url = city_info["url"]
    print(f"🔄 正在抓取 {city} YouBike 資料...")
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        raw = resp.json()
        
        # 處理不同縣市的回傳格式
        stations = []
        
        # 1. 處理桃園格式 (包含在 result -> records 中)
        if "result" in raw and "records" in raw["result"]:
            raw_list = raw["result"]["records"]
        # 2. 處理高雄格式 (包含在 data 中)
        elif "data" in raw and isinstance(raw["data"], list):
            raw_list = raw["data"]
        # 3. 處理台北/新北/台中格式 (直接是 List 或 Dict)
        elif isinstance(raw, dict):
            raw_list = list(raw.values()) if city == "台北市" else raw.get("retVal", [])
            if not raw_list and not isinstance(raw, list): raw_list = [raw]
        else:
            raw_list = raw

        for s in raw_list:
            # 統一欄位名稱（YouBike 2.0 常見欄位名）
            stations.append({
                "id": str(s.get("sno", s.get("station_no", s.get("sna", "")))),
                "name": s.get("sna", s.get("station_name", {}).get("zh_tw", s.get("name_tw", ""))).replace("YouBike2.0_", ""),
                "city": city,
                "lat": float(s.get("lat", s.get("latitude", 0))),
                "lng": float(s.get("lng", s.get("longitude", 0))),
                "total": int(s.get("tot", s.get("total", 0))),
                "available_bikes": int(s.get("sbi", s.get("available_rent_bikes", 0))),
                "available_spaces": int(s.get("bemp", s.get("available_return_bikes", 0))),
            })
        return stations
    except Exception as e:
        print(f"⚠️ {city} 抓取失敗: {e}")
        return []


def fetch_all_youbike() -> dict:
    """平行抓取所有縣市資料並合併"""
    all_stations = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetch_city_data, city) for city in CITY_SOURCES]
        for future in concurrent.futures.as_completed(futures):
            all_stations.extend(future.result())

    return {
        "updated_at": datetime.now(TW_TZ).isoformat(),
        "total_stations": len(all_stations),
        "stations": all_stations,
    }


def main():
    try:
        data = fetch_all_youbike()
        if data["total_stations"] == 0:
            raise Exception("所有縣市抓取皆失敗，請檢查網路或端點。")
            
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✅ 全台 YouBike 資料寫入完成，共 {data['total_stations']} 站")
    except Exception as e:
        print(f"❌ 抓取失敗：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
