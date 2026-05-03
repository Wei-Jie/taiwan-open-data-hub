# 🛡️ AISDLC Skill: 系統安全性與強健性初始化 (Project Hardening Baseline)

> **版本**：v1.0  
> **目標**：在專案初始化或新功能開發階段，強制進行非功能性需求（NFR）與安全性檢核，確保系統具備商業級的穩定性。

---

## 🧭 觸發時機

1.  **專案啟動 (Project Init)**：建立新專案目錄後。
2.  **架構設計 (System Design)**：在撰寫 `System_Formal_Specification.md` 前。
3.  **核心重構 (Refactoring)**：涉及 API 通訊、資料庫寫入或身分驗證的重構。

---

## 📋 核心檢核範疇 (The "Must-Have" List)

當此 Skill 啟用時，Agent 必須引導用戶確認以下範疇的實作層級：

### 1. 併發與資源保護 (Concurrency & Resource Protection)
*   **[ ] 資源鎖定 (Locking)**：是否有多人同時操作同一資料導致 Race Condition 的風險？（如：GAS `LockService`）。
*   **[ ] 自動編號完整性**：流水編號是否可能重疊？

### 2. 流量與防禦 (Rate Limiting & Defense)
*   **[ ] API 限流 (Rate Limit)**：是否需要限制單一用戶/IP 在特定時間內的請求次數？
*   **[ ] CORS 來源檢查**：是否限制僅允許特定的 Domain（如 `localhost`, `github.io`）存取後端？
*   **[ ] 輸入驗證 (Input Validation)**：後端是否對所有傳入參數進行型別與長度檢查？

### 3. 維運監控與穩定性 (Observability & Stability)
*   **[ ] 全域錯誤攔截 (Global Catch)**：系統崩潰時是否能回傳友好的 JSON 錯誤而非原始堆疊？
*   **[ ] 系統日誌 (System Logs)**：是否具備獨立的日誌表/檔案記錄關鍵動作與 Error Stack？
*   **[ ] 欄位映射強健性 (Schema Adapter)**：資料表欄位順序改變時，程式是否會崩潰？（是否需要動態 Header Mapping）。

### 4. 環境與敏感資訊 (Environment & Secrets)
*   **[ ] 金鑰管理**：`.env` 是否已加入 `.gitignore`？是否有提供 `.env.example`？
*   **[ ] 敏感資料過濾**：Log 中是否會不經意記錄用戶密碼或手機號碼？

---

## 🛠️ 執行流程 (Workflow)

### Step 1: 偵測與提問
Agent 在載入此 Skill 後，應主動掃描技術棧並提出確認清單：
> 「偵測到您正在進行 [技術棧] 專案初始化。為確保系統穩定性，請確認以下安全性組件的實作範圍：...」

### Step 2: 產生 Baseline 代碼
根據用戶勾選，Agent 應自動產生或注入以下模板：
*   `withLock` 封裝函數 (適用於 GAS/Node.js)
*   `checkRateLimit` 攔截器
*   `GlobalErrorHandler` 模組
*   `SchemaAdapter` 欄位映射器

### Step 3: 更新規格文件
將確認的安全性規則寫入專案的 `doc/aisdlc_gen/00_System_Formal_Specification.md`。

---

## 📦 參考實作 (以 GAS 為例)

這些是從 `JWKL_CUISINE` 專案中提取的標準實作，可供新專案參考：

### A. 併發鎖定模板
```javascript
function withScriptLock(fn) {
  return function(...args) {
    const lock = LockService.getScriptLock();
    try {
      lock.waitLock(10000); // 等待 10 秒
      return fn(...args);
    } finally {
      lock.releaseLock();
    }
  };
}
```

### B. 限流機制模板
```javascript
function checkRateLimit(key, limit, period) {
  const cache = CacheService.getScriptCache();
  const count = parseInt(cache.get(key) || "0");
  if (count >= limit) throw new Error("Too many requests");
  cache.put(key, (count + 1).toString(), period);
}
```

### C. Schema Adapter (資料表欄位映射) 模板
```javascript
/**
 * 自動映射標題列索引，防止手動插入欄位導致程式抓錯位置
 * @param {Sheet} sheet 
 * @returns {Object} 映射表，例如 { id: 0, phone: 2 }
 */
function getHeaderMap(sheet) {
  const headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  const map = {};
  headers.forEach((h, i) => {
    const title = String(h).trim();
    if (title.includes("ID") || title === "id") map.uuid = i;
    if (title.includes("編號")) map.id = i;
    if (title.includes("電話") || title.includes("手機")) map.phone = i;
    if (title.includes("狀態")) map.status = i;
    // ... 根據需求擴充
  });
  
  // 核心檢核：確保關鍵欄位存在
  if (map.id === undefined) throw new Error("表格缺少必要欄位: [編號]");
  return map;
}

// 使用範例：
// const hMap = getHeaderMap(sheet);
// const orderId = row[hMap.id]; // 永遠能抓到正確的「編號」欄位
```

---

*Skill 編號：SKILL-SEC-001*  
*歸屬框架：AISDLC v2.0*
