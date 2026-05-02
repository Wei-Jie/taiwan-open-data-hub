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

    document.getElementById('taiexDate').textContent = t.date || '--';
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

    document.getElementById('taiexOpen').textContent =
      t.open ? Number(t.open).toLocaleString('zh-TW') : '--';
    document.getElementById('taiexHigh').textContent =
      t.high ? Number(t.high).toLocaleString('zh-TW') : '--';
    document.getElementById('taiexLow').textContent =
      t.low ? Number(t.low).toLocaleString('zh-TW') : '--';

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
    if (!data.rates || data.rates.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" class="loading-text">暫無資料</td></tr>';
      return;
    }

    tbody.innerHTML = data.rates.map(r => `
      <tr>
        <td>
          <div class="currency-code">${r.code}</div>
          <div class="currency-name">${r.name}</div>
        </td>
        <td>${r.buy_cash || '--'}</td>
        <td>${r.sell_cash || '--'}</td>
        <td>${r.buy_spot || '--'}</td>
        <td>${r.sell_spot || '--'}</td>
      </tr>
    `).join('');

  } catch (e) {
    console.error('匯率資料載入失敗：', e);
    document.getElementById('rateTableBody').innerHTML =
      '<tr><td colspan="5" class="loading-text">載入失敗</td></tr>';
  }
}

// ── 加密貨幣 ──
async function loadCryptoData() {
  try {
    const res = await fetch('./data/finance/crypto.json');
    const data = await res.json();

    document.getElementById('cryptoUpdated').textContent = formatUpdatedAt(data.updated_at);

    const tbody = document.getElementById('cryptoTableBody');
    if (!data.coins || data.coins.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" class="loading-text">暫無資料</td></tr>';
      return;
    }

    tbody.innerHTML = data.coins.map(c => {
      const isUp = c.change_24h >= 0;
      const changeClass = isUp ? 'change-up' : 'change-down';
      const changeSign = isUp ? '▲' : '▼';

      return `
        <tr>
          <td>${c.rank}</td>
          <td>
            <div class="coin-info">
              <img class="coin-img" src="${c.image}" alt="${c.symbol}" onerror="this.style.display='none'" />
              <div>
                <div class="coin-name">${c.name}</div>
                <div class="coin-symbol">${c.symbol}</div>
              </div>
            </div>
          </td>
          <td>$${Number(c.price_usd).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
          <td class="${changeClass}">${changeSign} ${Math.abs(c.change_24h).toFixed(2)}%</td>
          <td>${formatMarketCap(c.market_cap)}</td>
          <td>${formatMarketCap(c.volume_24h)}</td>
        </tr>
      `;
    }).join('');

  } catch (e) {
    console.error('加密貨幣資料載入失敗：', e);
    document.getElementById('cryptoTableBody').innerHTML =
      '<tr><td colspan="6" class="loading-text">載入失敗</td></tr>';
  }
}
