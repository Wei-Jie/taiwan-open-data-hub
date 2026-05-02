"""
fetch_crypto.py
抓取加密貨幣市值前 10 名資料（CoinGecko 免費 API，免金鑰）
更新頻率：每日 16:30（由 GitHub Actions 觸發）
"""
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests

COINGECKO_URL = (
    "https://api.coingecko.com/api/v3/coins/markets"
    "?vs_currency=usd&order=market_cap_desc&per_page=10&page=1"
    "&sparkline=false&price_change_percentage=24h"
)

OUTPUT_PATH = Path(__file__).parent.parent / "data" / "finance" / "crypto.json"
TW_TZ = timezone(timedelta(hours=8))


def fetch_crypto() -> dict:
    """抓取加密貨幣市值 Top 10"""
    print("🔄 正在抓取加密貨幣資料...")

    headers = {"Accept": "application/json"}
    resp = requests.get(COINGECKO_URL, headers=headers, timeout=30)
    resp.raise_for_status()
    raw = resp.json()

    coins = []
    for item in raw:
        coins.append({
            "rank": item.get("market_cap_rank", 0),
            "id": item.get("id", ""),
            "symbol": item.get("symbol", "").upper(),
            "name": item.get("name", ""),
            "image": item.get("image", ""),
            "price_usd": item.get("current_price", 0),
            "market_cap": item.get("market_cap", 0),
            "change_24h": round(item.get("price_change_percentage_24h", 0) or 0, 2),
            "high_24h": item.get("high_24h", 0),
            "low_24h": item.get("low_24h", 0),
            "volume_24h": item.get("total_volume", 0),
        })

    return {
        "updated_at": datetime.now(TW_TZ).isoformat(),
        "vs_currency": "USD",
        "coins": coins,
    }


def main():
    try:
        data = fetch_crypto()
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✅ 加密貨幣資料寫入完成，共 {len(data['coins'])} 種")
    except Exception as e:
        print(f"❌ 抓取失敗：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
