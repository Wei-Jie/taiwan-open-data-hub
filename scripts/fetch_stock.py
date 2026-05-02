"""
fetch_stock.py
抓取台灣加權指數當日資料（TWSE 開放 API，免金鑰）
更新頻率：週一至週五 16:30（由 GitHub Actions 觸發）
"""
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests

# TWSE 大盤指數（加權股價指數）
TWSE_URL = "https://openapi.twse.com.tw/v1/exchangeReport/FMTQIK"
# TWSE 近 30 日成交資訊
TWSE_HISTORY_URL = "https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL"

OUTPUT_PATH = Path(__file__).parent.parent / "data" / "finance" / "stock_index.json"
TW_TZ = timezone(timedelta(hours=8))


def fetch_stock() -> dict:
    """抓取台灣大盤指數（取最新一個交易日）"""
    print("🔄 正在抓取台灣加權指數...")

    resp = requests.get(TWSE_URL, timeout=30)
    resp.raise_for_status()
    raw = resp.json()

    # FMTQIK 回傳近 20 個交易日資料，取最後一筆（最新）
    # 欄位：Date, TradeVolume, TradeValue, Transaction, TAIEX, Change
    taiex = raw[-1] if raw else None

    # 計算漲跌百分比（API 未提供，由 TAIEX 和 Change 推算）
    change_pct = ""
    if taiex:
        try:
            close_val = float(taiex.get("TAIEX", 0))
            change_val = float(taiex.get("Change", 0))
            prev_close = close_val - change_val
            if prev_close != 0:
                change_pct = f"{change_val / prev_close * 100:.2f}"
        except (ValueError, ZeroDivisionError):
            pass

    return {
        "updated_at": datetime.now(TW_TZ).isoformat(),
        "taiex": {
            "name": "台灣加權指數",
            "date": taiex.get("Date", "") if taiex else "",
            "close": taiex.get("TAIEX", "") if taiex else "",
            "change": taiex.get("Change", "") if taiex else "",
            "change_pct": change_pct,
            "trade_volume": taiex.get("TradeVolume", "") if taiex else "",
            "trade_value": taiex.get("TradeValue", "") if taiex else "",
        },
        "raw_count": len(raw),
    }


def main():
    try:
        data = fetch_stock()
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✅ 台灣加權指數資料寫入完成")
    except Exception as e:
        print(f"❌ 抓取失敗：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
