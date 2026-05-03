# Taiwan Open Data Hub - 執行計畫 (Implementation Plan)

## 1. 目標
本階段目標在於補完全台灣 YouBike 資料同步，並開始規劃新的資料模組（氣象、油價），同時優化前端使用者體驗。

## 2. 核心任務清單

### 2.1 YouBike 全台同步 (TDX 整合)
- [ ] 獲取並設定 `TDX_CLIENT_ID` 與 `TDX_CLIENT_SECRET` 於 GitHub Secrets。
- [ ] 執行 GitHub Actions 手動測試，驗證全台縣市資料是否能正確合併。
- [ ] 修正前端地圖縮放等級 (Zoom Level)，確保使用者能流暢切換不同縣市。

### 2.2 氣象資料模組 (新功能)
- [ ] 調研「氣象署開放資料平台」API（如：F-C0032-001 縣市預報）。
- [ ] 撰寫 `scripts/fetch_weather.py`。
- [ ] 前端實作「天氣」卡片與圖層切換。

### 2.3 UI/UX 優化
- [ ] **地圖彈窗樣式**：美化 YouBike 與 AQI 的地圖 Popup，加入顏色標籤（如 AQI 等級顏色）。
- [ ] **深色模式微調**：確保所有卡片在深色模式下的閱讀舒適度。

## 3. 驗證計畫
- **自動化測試**：確認所有 Workflow 均能順利執行並 commit 資料。
- **資料正確性**：比對網頁顯示數值與原始 API 來源是否一致。
- **效能驗證**：檢查 JSON 檔案大小，若 YouBike 全台站點過多（> 1MB），考慮進行分縣市加載或壓縮。

## 4. 使用者審閱點 (User Review Points)
- 🔴 TDX 金鑰生效後的資料完整度確認。
- 🔴 氣象卡片設計樣式確認。
