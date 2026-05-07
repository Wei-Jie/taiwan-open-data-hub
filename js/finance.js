/* finance.js - 財經資料：加權指數、匯率、加密貨幣 */

async function loadFinanceData() {
  await Promise.all([
    loadStockData(),
    loadExchangeRate(),
    loadCryptoData(),
  ]);
}

let allStocksData = []; // 全台股精簡資料庫

// ── 台灣加權指數與個股資訊 ──
async function loadStockData() {
  try {
    const [resIndex, resAll] = await Promise.all([
      fetch('./data/finance/stock_index.json'),
      fetch('./data/finance/all_stocks.json').catch(() => null)
    ]);
    
    const data = await resIndex.json();
    if (resAll && resAll.ok) {
      allStocksData = await resAll.json();
    }
    
    const t = data.taiex || {};

    document.getElementById('taiexDate').textContent = t.date
      ? formatRocDate(t.date)
      : '--';
    document.getElementById('taiexClose').textContent =
      t.close ? Number(t.close).toLocaleString('zh-TW') : '--';

    if (t.change) {
      const changeNum = parseFloat(t.change);
      const isUp = changeNum >= 0;
      const sign = isUp ? '▲' : '▼';
      const pct = t.change_pct ? `(${t.change_pct}%)` : '';
      const el = document.getElementById('taiexChange');
      el.textContent = `${sign} ${Math.abs(changeNum).toLocaleString('zh-TW')} ${pct}`;
      el.className = `taiex-change ${isUp ? 'up' : 'down'}`;
    }

    // 成交量（張）與成交金額（元）
    document.getElementById('taiexVolume').textContent =
      t.trade_volume ? `${(Number(t.trade_volume) / 1e8).toFixed(2)} 億張` : '--';
    document.getElementById('taiexValue').textContent =
      t.trade_value ? `${(Number(t.trade_value) / 1e8).toFixed(0)} 億元` : '--';

    // 渲染 Top 10 表格
    renderStockTable('topStockTableBody', data.top_stocks);
    renderStockTable('topEtfTableBody', data.top_etfs);
    
    // 渲染 UI 觀察名單
    renderWatchlist();

  } catch (e) {
    console.error('股市資料載入失敗：', e);
  }
}

// ── UI 觀察名單控制邏輯 ──
const DEFAULT_WATCHLIST = ["2330", "2317", "2454", "2308", "2881"];

function getWatchlistCodes() {
  const saved = localStorage.getItem('myWatchlist');
  return saved ? JSON.parse(saved) : DEFAULT_WATCHLIST;
}

function saveWatchlistCodes(codes) {
  localStorage.setItem('myWatchlist', JSON.stringify(codes));
}

function renderWatchlist() {
  const codes = getWatchlistCodes();
  // 從 allStocksData 挑出符合的股票，若找不到則回傳假資料表示該股票不存在或下市
  const watchlistData = codes.map(code => {
    const found = allStocksData.find(s => s.c === code || s.Code === code); // 支援新舊格式
    if (found) {
      return { Code: found.c || found.Code, Name: found.n || found.Name, ClosingPrice: found.p || found.ClosingPrice, Change: found.cg || found.Change, TradeVolume: found.v || found.TradeVolume };
    }
    return { Code: code, Name: '未知代號', ClosingPrice: '0', Change: '0', TradeVolume: '0' };
  });
  
  renderStockTable('watchlistTableBody', watchlistData, true);
}

function addWatchlist() {
  const input = document.getElementById('watchInput');
  const code = input.value.trim();
  if (!code) return;
  
  const codes = getWatchlistCodes();
  if (!codes.includes(code)) {
    // 驗證代號是否存在
    const exists = allStocksData.some(s => s.c === code || s.Code === code);
    if (!exists && allStocksData.length > 0) {
      alert(`找不到股票代號：${code}`);
      return;
    }
    codes.push(code);
    saveWatchlistCodes(codes);
    renderWatchlist();
  }
  input.value = '';
}

function removeWatchlist(code) {
  let codes = getWatchlistCodes();
  codes = codes.filter(c => c !== code);
  saveWatchlistCodes(codes);
  renderWatchlist();
}

function renderStockTable(tbodyId, stocks, isWatchlist = false) {
  const tbody = document.getElementById(tbodyId);
  if (!tbody) return;
  tbody.innerHTML = '';
  
  if (!stocks || stocks.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" class="loading-text">暫無資料</td></tr>';
    return;
  }
  
  stocks.forEach(s => {
    const tr = document.createElement('tr');
    
    // 判斷漲跌
    const changeVal = parseFloat(s.Change || s.cg) || 0;
    const isUp = changeVal > 0;
    const isDown = changeVal < 0;
    let changeClass = '';
    let changeSign = '';
    
    if (isUp) {
      changeClass = 'change-up';
      changeSign = '▲';
    } else if (isDown) {
      changeClass = 'change-down';
      changeSign = '▼';
    }
    
    const code = s.Code || s.c;
    const name = s.Name || s.n;
    const price = s.ClosingPrice || s.p;
    
    const tdCode = document.createElement('td');
    tdCode.innerHTML = `<div class="currency-code">${code}</div>`;
    
    const tdName = document.createElement('td');
    tdName.textContent = name;
    
    const tdPrice = document.createElement('td');
    tdPrice.textContent = price;
    
    const tdChange = document.createElement('td');
    tdChange.className = changeClass;
    tdChange.textContent = changeSign ? `${changeSign} ${Math.abs(changeVal)}` : '0.00';
    
    const tdVolume = document.createElement('td');
    if (isWatchlist) {
      const btn = document.createElement('button');
      btn.textContent = '❌';
      btn.style.cssText = 'background:transparent; border:none; cursor:pointer; font-size:12px;';
      btn.onclick = () => removeWatchlist(code);
      tdVolume.appendChild(btn);
    } else {
      const vol = parseInt(s.TradeVolume || s.v) || 0;
      tdVolume.textContent = `${(vol / 10000).toLocaleString('zh-TW')} 張`;
    }
    
    tr.append(tdCode, tdName, tdPrice, tdChange, tdVolume);
    tbody.appendChild(tr);
  });
}

// ── 匯率 ──
async function loadExchangeRate() {
  try {
    const res = await fetch('./data/finance/exchange_rate.json');
    const data = await res.json();

    document.getElementById('rateUpdated').textContent = formatUpdatedAt(data.updated_at);

    const tbody = document.getElementById('rateTableBody');
    tbody.innerHTML = ''; // 清空內容

    if (!data.rates || data.rates.length === 0) {
      const tr = document.createElement('tr');
      tr.innerHTML = '<td colspan="5" class="loading-text">暫無資料</td>';
      tbody.appendChild(tr);
      return;
    }

    data.rates.forEach(r => {
      const tr = document.createElement('tr');
      
      // 使用安全的賦值方式
      const tdInfo = document.createElement('td');
      tdInfo.innerHTML = `<div class="currency-code">${r.code}</div><div class="currency-name">${r.name}</div>`;
      
      const tdBuyCash = document.createElement('td');
      tdBuyCash.textContent = r.buy_cash || '--';
      
      const tdSellCash = document.createElement('td');
      tdSellCash.textContent = r.sell_cash || '--';
      
      const tdBuySpot = document.createElement('td');
      tdBuySpot.textContent = r.buy_spot || '--';
      
      const tdSellSpot = document.createElement('td');
      tdSellSpot.textContent = r.sell_spot || '--';
      
      tr.append(tdInfo, tdBuyCash, tdSellCash, tdBuySpot, tdSellSpot);
      tbody.appendChild(tr);
    });

  } catch (e) {
    console.error('匯率資料載入失敗：', e);
    const tbody = document.getElementById('rateTableBody');
    tbody.innerHTML = '<tr><td colspan="5" class="loading-text">載入失敗</td></tr>';
  }
}

// ── 加密貨幣 ──
async function loadCryptoData() {
  try {
    const res = await fetch('./data/finance/crypto.json');
    const data = await res.json();

    document.getElementById('cryptoUpdated').textContent = formatUpdatedAt(data.updated_at);

    const tbody = document.getElementById('cryptoTableBody');
    tbody.innerHTML = ''; // 清空內容

    if (!data.coins || data.coins.length === 0) {
      const tr = document.createElement('tr');
      tr.innerHTML = '<td colspan="6" class="loading-text">暫無資料</td>';
      tbody.appendChild(tr);
      return;
    }

    data.coins.forEach(c => {
      const isUp = c.change_24h >= 0;
      const changeClass = isUp ? 'change-up' : 'change-down';
      const changeSign = isUp ? '▲' : '▼';

      const tr = document.createElement('tr');
      
      const tdRank = document.createElement('td');
      tdRank.textContent = c.rank;
      
      const tdCoin = document.createElement('td');
      tdCoin.innerHTML = `
        <div class="crypto-info">
          <img src="${c.image}" class="crypto-icon" alt="${c.symbol}" onerror="this.src='https://via.placeholder.com/20'">
          <span class="crypto-symbol">${c.symbol}</span>
        </div>
      `;

      const tdPrice = document.createElement('td');
      tdPrice.textContent = `$${Number(c.price_usd).toLocaleString()}`;
      
      const tdMarketCap = document.createElement('td');
      tdMarketCap.textContent = `$${(Number(c.market_cap) / 1e9).toFixed(1)} B`;
      
      const tdChange = document.createElement('td');
      tdChange.className = changeClass;
      tdChange.textContent = `${changeSign} ${Math.abs(c.change_24h)}%`;
      
      const tdVolume = document.createElement('td');
      tdVolume.textContent = `$${(Number(c.volume_24h) / 1e6).toFixed(1)} M`;

      tr.append(tdRank, tdCoin, tdPrice, tdMarketCap, tdChange, tdVolume);
      tbody.appendChild(tr);
    });

  } catch (e) {
    console.error('加密貨幣資料載入失敗：', e);
    const tbody = document.getElementById('cryptoTableBody');
    tbody.innerHTML = '<tr><td colspan="6" class="loading-text">載入失敗</td></tr>';
  }
}
