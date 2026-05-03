# Taiwan Open Data Hub - 安全性優化計畫 (Security Hardening Plan)

## 1. 憑證與敏感資訊保護 (Secrets Management)
- **現狀**：API Key 已開始轉向環境變數，但代碼歷史中可能有殘留。
- **行動**：
    - [ ] **徹底移除 Hardcoded Keys**：檢查所有腳本（如 `fetch_stock.py`, `fetch_crypto.py`），確保沒有任何 API Key 直接寫在程式碼中。
    - [ ] **清理 Git 歷史 (可選)**：若舊的 Key 具備高度敏感性（如帶有付費權限），建議使用 `git-filter-repo` 或 BFG Repo-Cleaner 清理歷史紀錄，或乾脆在 API 端更換新的 Key。

## 2. 腳本健壯性與資料驗證 (Script Security)
- **現狀**：目前腳本對 API 回傳的資料內容信任度較高。
- **行動**：
    - [ ] **嚴格的類型檢查**：在解析 JSON 後，先驗證資料格式（例如：數值欄位是否真的是數字），防止惡意或毀損的 API 內容導致腳本報錯。
    - [ ] **Timeout 與重試機制**：為所有 `requests.get()` 加入明確的 `timeout` 參數（已初步實作），並考慮加入 `urllib3` 的重試邏輯，防止網路不穩導致的 Workflow 頻繁失敗。

## 3. 前端防禦 (Frontend Security)
- **現狀**：使用 `innerHTML` 或直接賦值。
- **行動**：
    - [ ] **防止 XSS 攻擊**：檢查 `js/finance.js` 與 `js/transport.js`，將所有用於顯示文字的欄位改用 `.textContent` 或 `.innerText`，避免瀏覽器將資料當作 HTML 指令執行。
    - [ ] **Content Security Policy (CSP)**：在 `index.html` 加入 CSP Meta 標籤，限制僅能向白名單內的域名（如台銀、環境部、TDX）請求資料。

## 4. 自動化環境安全 (Action Security)
- **行動**：
    - [ ] **限制 GitHub Actions 權限**：將 `permissions: contents: write` 限制在必要的 Job 中。
    - [ ] **依賴更新**：使用 `dependabot` 自動追蹤 `requests` 等 Python 套件的安全性更新。

## 5. 安全性檢查表 (QA Checklist)
- [ ] 執行 `git grep` 搜尋是否有任何類似 "key", "token", "password" 的敏感字串。
- [ ] 模擬 API 回傳惡意內容，測試前端是否會執行 Script。
