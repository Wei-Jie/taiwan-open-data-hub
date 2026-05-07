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
ALL_STOCKS_OUTPUT = Path(__file__).parent.parent / "data" / "finance" / "all_stocks.json"
TW_TZ = timezone(timedelta(hours=8))

def fetch_stock() -> dict:
    """抓取台灣大盤指數與個股資訊"""
    print("🔄 正在抓取台灣加權指數...")

    # 1. 抓取大盤
    try:
        resp = requests.get(TWSE_URL, timeout=30)
        resp.raise_for_status()
        raw_taiex = resp.json()
    except Exception as e:
        print(f"⚠️ 大盤抓取失敗: {e}")
        raw_taiex = []

    taiex = raw_taiex[-1] if raw_taiex else None
    change_pct = ""
    if taiex:
        try:
            close_val = float(taiex.get("TAIEX", 0).replace(",", ""))
            change_val = float(taiex.get("Change", 0).replace(",", ""))
            prev_close = close_val - change_val
            if prev_close != 0:
                change_pct = f"{change_val / prev_close * 100:.2f}"
        except (ValueError, ZeroDivisionError):
            pass

    # 2. 抓取個股每日收盤行情
    print("🔄 正在抓取個股收盤行情...")
    top_stocks = []
    top_etfs = []
    all_stocks_list = []
    
    try:
        stock_resp = requests.get("https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL", timeout=30)
        stock_resp.raise_for_status()
        raw_stocks = stock_resp.json()
        
        # 轉換型別以利排序
        valid_stocks = []
        for s in raw_stocks:
            try:
                s['TradeVolumeInt'] = int(s.get('TradeVolume', 0))
                valid_stocks.append(s)
            except ValueError:
                pass
                
        # 依成交量降冪排序
        valid_stocks.sort(key=lambda x: x['TradeVolumeInt'], reverse=True)
        
        for s in valid_stocks:
            code = s.get('Code', '')
            
            # 建立精簡版全台股清單供前端 UI 使用
            # 欄位：c:代號, n:名稱, p:收盤價, cg:漲跌, v:成交量
            all_stocks_list.append({
                "c": code,
                "n": s.get('Name', ''),
                "p": s.get('ClosingPrice', ''),
                "cg": s.get('Change', ''),
                "v": str(s.get('TradeVolumeInt', 0))
            })
                
            # 分類 ETF 與 個股 (ETF 在 TWSE 代號通常為 00 開頭)
            if code.startswith('00'):
                if len(top_etfs) < 10:
                    top_etfs.append(s)
            else:
                if len(top_stocks) < 10:
                    top_stocks.append(s)
                    
    except Exception as e:
        print(f"⚠️ 個股資料抓取失敗: {e}")

    # 寫入 all_stocks.json
    try:
        ALL_STOCKS_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        ALL_STOCKS_OUTPUT.write_text(json.dumps(all_stocks_list, ensure_ascii=False, separators=(',', ':')), encoding="utf-8")
        print(f"✅ 全台股精簡資料庫寫入完成，共 {len(all_stocks_list)} 筆")
    except Exception as e:
        print(f"⚠️ 全台股精簡資料庫寫入失敗: {e}")

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
        "top_stocks": top_stocks,
        "top_etfs": top_etfs,
        "raw_count": len(raw_taiex),
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
