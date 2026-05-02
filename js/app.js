/* app.js - 主控制：Tab 切換邏輯 */

document.addEventListener('DOMContentLoaded', () => {
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabSections = document.querySelectorAll('.tab-section');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.tab;

      // 切換按鈕狀態
      tabBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      // 切換內容區域
      tabSections.forEach(section => {
        section.classList.add('hidden');
        section.classList.remove('active');
      });

      const targetSection = document.getElementById(`tab-${target}`);
      if (targetSection) {
        targetSection.classList.remove('hidden');
        targetSection.classList.add('active');

        // 地圖需要在顯示後重新計算尺寸
        if (target === 'transport' && window._map) {
          setTimeout(() => window._map.invalidateSize(), 100);
        }

        // 財經 Tab 載入資料
        if (target === 'finance' && !window._financeLoaded) {
          loadFinanceData();
          window._financeLoaded = true;
        }
      }
    });
  });

  // 格式化數字（加千分位）
  window.formatNumber = (num, decimals = 0) => {
    if (num == null || isNaN(num)) return '--';
    return Number(num).toLocaleString('zh-TW', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });
  };

  // 格式化市值（億/兆）
  window.formatMarketCap = (num) => {
    if (!num) return '--';
    if (num >= 1e12) return `$${(num / 1e12).toFixed(2)}T`;
    if (num >= 1e9) return `$${(num / 1e9).toFixed(2)}B`;
    if (num >= 1e6) return `$${(num / 1e6).toFixed(2)}M`;
    return `$${num}`;
  };

  // 格式化更新時間
  window.formatUpdatedAt = (isoStr) => {
    if (!isoStr) return '未知';
    try {
      const d = new Date(isoStr);
      return d.toLocaleString('zh-TW', { timeZone: 'Asia/Taipei', hour12: false });
    } catch {
      return isoStr;
    }
  };

  // 格式化民國日期字串（TWSE 格式：1150401 → 2026/04/01）
  window.formatRocDate = (rocStr) => {
    if (!rocStr || rocStr.length < 7) return rocStr || '--';
    const year = parseInt(rocStr.slice(0, rocStr.length - 4), 10) + 1911;
    const month = rocStr.slice(-4, -2);
    const day = rocStr.slice(-2);
    return `${year}/${month}/${day}`;
  };
});
