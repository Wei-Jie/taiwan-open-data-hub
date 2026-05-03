/* finance.js - 財經資料：加權指數、匯率、加密貨幣 */

async function loadFinanceData() {
  await Promise.all([
    loadStockData(),
    loadExchangeRate(),
    loadCryptoData(),
  ]);
}

// ── 台灣加權指數 ──
async function loadStockData() {
  try {
    const res = await fetch('./data/finance/stock_index.json');
    const data = await res.json();
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

  } catch (e) {
    console.error('股市資料載入失敗：', e);
  }
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
