"""
fetch_exchange_rate.py
抓取台灣銀行每日牌告匯率（CSV 格式，免金鑰）
更新頻率：週一至週五 16:30（由 GitHub Actions 觸發）
"""
import csv
import io
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests

# 台灣銀行牌告匯率 CSV
BOT_URL = "https://rate.bot.com.tw/xrt/flcsv/0/day"

OUTPUT_PATH = Path(__file__).parent.parent / "data" / "finance" / "exchange_rate.json"
TW_TZ = timezone(timedelta(hours=8))

# 主要貨幣代號對應
CURRENCY_NAMES = {
    "USD": "美元",
    "EUR": "歐元",
    "JPY": "日圓",
    "GBP": "英鎊",
    "AUD": "澳幣",
    "CAD": "加拿大幣",
    "CNY": "人民幣",
    "HKD": "港幣",
    "SGD": "新加坡幣",
    "KRW": "韓元",
}


def fetch_exchange_rate() -> dict:
    """抓取台灣銀行每日牌告匯率"""
    print("🔄 正在抓取台灣銀行匯率...")

    resp = requests.get(BOT_URL, timeout=30)
    resp.raise_for_status()

    # 台灣銀行 CSV 使用 Big5 編碼
    content = resp.content.decode("big5", errors="replace")
    reader = csv.reader(io.StringIO(content))

    rates = []
    for row in reader:
        if len(row) < 5:
            continue
        code = row[0].strip()
        if code not in CURRENCY_NAMES:
            continue
        try:
            rates.append({
                "code": code,
                "name": CURRENCY_NAMES[code],
                "buy_cash": row[1].strip(),   # 現金買入
                "sell_cash": row[2].strip(),  # 現金賣出
                "buy_spot": row[3].strip(),   # 即期買入
                "sell_spot": row[4].strip(),  # 即期賣出
            })
        except IndexError:
            continue

    return {
        "updated_at": datetime.now(TW_TZ).isoformat(),
        "source": "台灣銀行",
        "base": "TWD",
        "rates": rates,
    }


def main():
    try:
        data = fetch_exchange_rate()
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✅ 匯率資料寫入完成，共 {len(data['rates'])} 種貨幣")
    except Exception as e:
        print(f"❌ 抓取失敗：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
