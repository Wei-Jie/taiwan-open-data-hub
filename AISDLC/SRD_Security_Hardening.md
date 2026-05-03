# 🛡️ 系統規格文件 (SRD)：後端安全性與架構加固 (v2.2)

本文件詳述 「小灶私廚 v2.2」 中實施的後端強化技術規格，旨在建立一個具備商業級穩定性的 GAS Serverless 架構。

## 1. 核心架構變更：Handler 模式
原有的 monolithic `doPost` 已重構為 **Action-based Handler 路由模式**。
- **優點**：解耦業務邏輯、簡化測試、提升可讀性。
- **主要分流**：`SUBMIT_CUSTOMER_ORDER`, `TRACK_ORDER`, `QUERY`, `CRUD`, `PING`。

## 2. 安全性實施 (Security Measures)

### 2.1 併發鎖定機制 (Lock Service)
- **實作方式**：在 `handleOrderSubmit` 中使用 `withScriptLock` 封裝。
- **規則**：後端會先取得全域 Script Lock (等待 10 秒)，成功後才讀取當前最大單號、生成新單號、並寫入。
- **目的**：杜絕同時兩筆訂單產生相同編號的資源競賽 (Race Condition)。

### 2.2 API 限流機制 (Rate Limit)
- **技術**：使用 `CacheService` 紀錄 Key。
- **參數**：
    - 送單：以 `submit:{phone}` 為憑，每 60 秒上限 10 次。
    - 查詢：以 `track:{phone}` 為憑，每 60 秒上限 20 次。
- **防禦**：防止惡意腳本頻繁查詢與灌單攻擊。

### 2.3 CORS 來源檢查
- **邏輯**：檢查請求中的 `Origin` 標頭。
- **白名單**：`wei-jie.github.io`, `localhost`。
- **警示**：非法來源的請求將在 `doPost` 的進入點被辨識。

## 3. 維運監控 (Observability)

### 3.1 自動化系統日誌 (System Logs)
- **觸發點**：`doPost` 的全域 `catch` 區域。
- **動作**：當發生後端崩潰時，呼叫 `logErrorToSheet`。
- **儲存**：Google Sheets 名稱為 `系統日誌`。包含時間、動作、錯誤堆疊。

---

## 4. 欄位自動映射 (Schema Adapter)
- **特性**：實作 `getHeaderMap` 函數。
- **邏輯**：每次查詢時動態讀取標題列並映射關鍵字（如「手機」對應 `phone`）。
- **優點**：解決手動在試算表插入欄位後導致程式抓錯資訊的問題。

---
*文件編號：v2.2-SRD-SEC*  
*最後更新：2026-04-23*
