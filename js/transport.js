/* transport.js - Leaflet 地圖：YouBike + AQI */

let map, youbikeLayer, aqiLayer;
let currentLayer = 'youbike';

// YouBike 顏色
function getYoubikeColor(available) {
  if (available >= 10) return '#4ade80';
  if (available >= 3)  return '#facc15';
  if (available >= 1)  return '#f97316';
  return '#64748b';
}

// AQI 顏色
function getAqiColor(aqi) {
  if (aqi <= 50)  return '#4ade80';
  if (aqi <= 100) return '#facc15';
  if (aqi <= 150) return '#f97316';
  if (aqi <= 200) return '#ef4444';
  if (aqi <= 300) return '#a855f7';
  return '#7f1d1d';
}

function circleMarker(latlng, color, radius = 7) {
  return L.circleMarker(latlng, {
    radius,
    fillColor: color,
    color: 'rgba(0,0,0,0.3)',
    weight: 1,
    opacity: 0.9,
    fillOpacity: 0.85,
  });
}

// 初始化地圖
document.addEventListener('DOMContentLoaded', async () => {
  map = L.map('map', { center: [23.97, 120.97], zoom: 7 });
  window._map = map;

  // 深色地圖底圖
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '© OpenStreetMap © CARTO',
    subdomains: 'abcd',
    maxZoom: 19,
  }).addTo(map);

  // 📍 加入定位功能按鈕
  const locateControl = L.control({position: 'topleft'});
  locateControl.onAdd = function (map) {
    const btn = L.DomUtil.create('button', 'leaflet-bar leaflet-control leaflet-control-custom');
    btn.innerHTML = '🎯';
    btn.style.backgroundColor = '#1e293b'; // 深色按鈕配合主題
    btn.style.color = '#fff';
    btn.style.width = '34px';
    btn.style.height = '34px';
    btn.style.lineHeight = '30px';
    btn.style.textAlign = 'center';
    btn.style.cursor = 'pointer';
    btn.style.border = '2px solid rgba(255,255,255,0.1)';
    btn.style.borderRadius = '4px';
    btn.style.fontSize = '18px';
    btn.title = "回到現在定位";

    // 懸停效果
    btn.onmouseover = () => btn.style.backgroundColor = '#334155';
    btn.onmouseout = () => btn.style.backgroundColor = '#1e293b';

    btn.onclick = function(e) {
      e.preventDefault();
      e.stopPropagation();
      map.locate({setView: true, maxZoom: 15});
    }
    return btn;
  };
  locateControl.addTo(map);

  // 處理定位成功：在地圖上標記當前位置
  let userMarker;
  map.on('locationfound', function(e) {
    if (userMarker) {
      userMarker.setLatLng(e.latlng);
    } else {
      userMarker = L.circleMarker(e.latlng, {
        radius: 8,
        fillColor: '#3b82f6', // 藍色標記
        color: '#ffffff',
        weight: 2,
        opacity: 1,
        fillOpacity: 1
      }).addTo(map);
      userMarker.bindPopup("📍 您的目前位置").openPopup();
    }
  });

  // 處理定位失敗
  map.on('locationerror', function(e) {
    alert("無法取得位置：" + e.message + " (請確認已允許瀏覽器存取位置資訊)");
  });

  youbikeLayer = L.layerGroup();
  aqiLayer = L.layerGroup();

  await loadYoubikeData();
  youbikeLayer.addTo(map);
});

// 切換圖層
window.switchLayer = function(layer) {
  currentLayer = layer;

  document.getElementById('btnYoubike').classList.toggle('active', layer === 'youbike');
  document.getElementById('btnAqi').classList.toggle('active', layer === 'aqi');

  document.getElementById('youbikeStats').classList.toggle('hidden', layer !== 'youbike');
  document.getElementById('aqiStats').classList.toggle('hidden', layer !== 'aqi');
  document.getElementById('aqiLegend').classList.toggle('hidden', layer !== 'aqi');

  if (layer === 'youbike') {
    map.removeLayer(aqiLayer);
    youbikeLayer.addTo(map);
  } else {
    map.removeLayer(youbikeLayer);
    loadAqiData().then(() => aqiLayer.addTo(map));
  }
};

// 載入 YouBike 資料
async function loadYoubikeData() {
  try {
    const res = await fetch('./data/transport/youbike.json');
    const data = await res.json();
    const stations = data.stations || [];

    youbikeLayer.clearLayers();

    let totalBikes = 0, totalSpaces = 0;

    stations.forEach(s => {
      if (!s.lat || !s.lng) return;
      totalBikes += s.available_bikes;
      totalSpaces += s.available_spaces;

      const color = getYoubikeColor(s.available_bikes);
      const marker = circleMarker([s.lat, s.lng], color);

      marker.bindPopup(`
        <div class="popup-title">🚲 ${s.name}</div>
        <div class="popup-row">
          <span>城市</span><span class="popup-val">${s.city || '--'}</span>
        </div>
        <div class="popup-row">
          <span>可借車輛</span><span class="popup-val" style="color:${color}">${s.available_bikes}</span>
        </div>
        <div class="popup-row">
          <span>可還空位</span><span class="popup-val">${s.available_spaces}</span>
        </div>
        <div class="popup-row">
          <span>站點容量</span><span class="popup-val">${s.total}</span>
        </div>
        <div style="margin-top: 12px; text-align: center;">
          <a href="${s.map_url || `https://www.google.com/maps/dir/?api=1&destination=${s.lat},${s.lng}`}" target="_blank" style="display: block; width: 100%; padding: 8px 0; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 14px; box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.3); transition: transform 0.2s, box-shadow 0.2s;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 8px -2px rgba(16, 185, 129, 0.4)';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 6px -1px rgba(16, 185, 129, 0.3)';">
            🚗 導航前往
          </a>
        </div>
      `);

      youbikeLayer.addLayer(marker);
    });

    // 更新統計卡片
    document.getElementById('totalStations').textContent = formatNumber(stations.length);
    document.getElementById('totalBikes').textContent = formatNumber(totalBikes);
    document.getElementById('totalSpaces').textContent = formatNumber(totalSpaces);
    document.getElementById('youbikeUpdated').textContent = formatUpdatedAt(data.updated_at);

  } catch (e) {
    console.error('YouBike 資料載入失敗：', e);
    document.getElementById('youbikeUpdated').textContent = '載入失敗';
  }
}

// 載入 AQI 資料
async function loadAqiData() {
  try {
    const res = await fetch('./data/transport/air_quality.json');
    const data = await res.json();
    const stations = data.stations || [];

    aqiLayer.clearLayers();

    let good = 0, moderate = 0, bad = 0;

    stations.forEach(s => {
      if (!s.lat || !s.lng) return;

      const color = getAqiColor(s.aqi);
      if (s.aqi <= 50) good++;
      else if (s.aqi <= 100) moderate++;
      else bad++;

      const marker = circleMarker([s.lat, s.lng], color, 9);

      marker.bindPopup(`
        <div class="popup-title">💨 ${s.site}（${s.county}）</div>
        <div class="popup-row">
          <span>AQI</span><span class="popup-val" style="color:${color}">${s.aqi} - ${s.level}</span>
        </div>
        <div class="popup-row">
          <span>PM2.5</span><span class="popup-val">${s.pm25 || '--'}</span>
        </div>
        <div class="popup-row">
          <span>PM10</span><span class="popup-val">${s.pm10 || '--'}</span>
        </div>
        <div class="popup-row">
          <span>更新時間</span><span class="popup-val">${s.publish_time || '--'}</span>
        </div>
      `);

      aqiLayer.addLayer(marker);
    });

    document.getElementById('aqiTotalStations').textContent = formatNumber(stations.length);
    document.getElementById('aqiGood').textContent = good;
    document.getElementById('aqiModerate').textContent = moderate;
    document.getElementById('aqiBad').textContent = bad;

  } catch (e) {
    console.error('AQI 資料載入失敗：', e);
  }
}
