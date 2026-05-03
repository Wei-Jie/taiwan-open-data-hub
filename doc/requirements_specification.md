# Taiwan Open Data Hub - 需求與規格說明書 (Requirements Specification)

## 1. 系統概觀
本專案旨在建立一個自動化的「台灣公開資料即時看板」，透過 GitHub Actions 定時執行 Python 腳本抓取開放資料，並以靜態網頁 (GitHub Pages) 呈現。系統採用無後端 (Serverless) 架構，利用 Git 倉庫作為資料存儲介質。

## 2. 系統範圍 (Project Scope)
- **資料來源**：政府開放資料 (Open Data)、台灣銀行匯率、環境部 API、交通部 TDX 平台、加密貨幣交易所 API。
- **目標用戶**：需要快速查看台灣即時交通與財經資訊的用戶。
- **核心價值**：零成本運行、自動更新、透明的資料存儲。

## 3. 已實現功能 (Current Features)

### 3.1 交通資料模組 (Transport Module)
- **YouBike 即時看板**：
    - 串接全台主要縣市 YouBike 2.0 站點資料。
    - 顯示站點名稱、位置、剩餘車輛與剩餘空位。
    - 具備多來源容錯機制與 TDX 整合能力（待金鑰啟用）。
- **AQI 空氣品質**：
    - 串接環境部 (MOENV) API v2。
    - 支援全台測站數據顯示（PM2.5, PM10, O3 等）。
    - 具備 AQI 等級視覺化（顏色區分）。

### 3.2 財經資料模組 (Finance Module)
- **台股加權指數**：
    - 顯示最新收盤指數、漲跌點數與百分比。
    - 支援成交量與成交金額顯示。
    - 自動處理休市與非交易時段顯示。
- **台灣銀行匯率**：
    - 顯示現金買入/賣出、即期買入/賣出。
    - 支援多種國際主要貨幣。
- **加密貨幣**：
    - 顯示市值排名前 10 的加密貨幣價格與即時走勢。

## 4. 系統技術架構
- **Frontend**: HTML5, Vanilla JavaScript, Leaflet.js (地圖), Chart.js (圖表)。
- **Backend (Automation)**: Python 3.11 + GitHub Actions。
- **Database**: Git-based JSON flat files。
- **Deployment**: GitHub Pages。

## 5. 待完成與後續規劃 (Backlog)
- [ ] **TDX 全台同步**：待用戶申請並設定 `TDX_CLIENT_ID` 與 `TDX_CLIENT_SECRET`。
- [ ] **氣象資訊整合**：增加氣象署即時天氣預報與雨量圖層。
- [ ] **油價資訊**：增加中油/台塑即時油價看板。
- [ ] **地圖互動強化**：優化地圖彈窗 (Popup) 樣式。
- [ ] **歷史趨勢圖表**：繪製股市或匯率的簡單走勢圖。
