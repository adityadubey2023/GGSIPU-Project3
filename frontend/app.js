// frontend/app.js

const API_BASE = "http://localhost:8000";

let currentData = [];
let activeSymbol = null;
let refreshTimer = null;

// ---- SYMBOL META FOR REGION & NICE NAMES ----
const SYMBOL_META = {
  // India
  "RELIANCE.NS": { region: "India", name: "Reliance Industries" },
  "TCS.NS": { region: "India", name: "Tata Consultancy Services" },
  "INFY.NS": { region: "India", name: "Infosys" },
  "HDFCBANK.NS": { region: "India", name: "HDFC Bank" },
  "ICICIBANK.NS": { region: "India", name: "ICICI Bank" },
  "SBIN.NS": { region: "India", name: "State Bank of India" },
  "AXISBANK.NS": { region: "India", name: "Axis Bank" },
  "KOTAKBANK.NS": { region: "India", name: "Kotak Mahindra Bank" },
  "ITC.NS": { region: "India", name: "ITC Ltd" },
  "LT.NS": { region: "India", name: "Larsen & Toubro" },
  "BHARTIARTL.NS": { region: "India", name: "Bharti Airtel" },
  "ASIANPAINT.NS": { region: "India", name: "Asian Paints" },
  "HCLTECH.NS": { region: "India", name: "HCL Technologies" },
  "WIPRO.NS": { region: "India", name: "Wipro" },
  "MARUTI.NS": { region: "India", name: "Maruti Suzuki" },
  "TITAN.NS": { region: "India", name: "Titan Company" },
  "ULTRACEMCO.NS": { region: "India", name: "UltraTech Cement" },
  "BAJFINANCE.NS": { region: "India", name: "Bajaj Finance" },
  "ADANIENT.NS": { region: "India", name: "Adani Enterprises" },
  "ADANIPORTS.NS": { region: "India", name: "Adani Ports" },

  // US
  "AAPL": { region: "United States", name: "Apple Inc." },
  "MSFT": { region: "United States", name: "Microsoft" },
  "GOOGL": { region: "United States", name: "Alphabet (Google)" },
  "AMZN": { region: "United States", name: "Amazon" },
  "META": { region: "United States", name: "Meta Platforms" },
  "TSLA": { region: "United States", name: "Tesla" },
  "NVDA": { region: "United States", name: "NVIDIA" },
  "NFLX": { region: "United States", name: "Netflix" },
  "JPM": { region: "United States", name: "JPMorgan Chase" },
  "V": { region: "United States", name: "Visa" },
  "MA": { region: "United States", name: "Mastercard" },
  "JNJ": { region: "United States", name: "Johnson & Johnson" },
  "UNH": { region: "United States", name: "UnitedHealth Group" },
  "PG": { region: "United States", name: "Procter & Gamble" },
  "DIS": { region: "United States", name: "Disney" },
  "INTC": { region: "United States", name: "Intel" },
  "CSCO": { region: "United States", name: "Cisco" },
  "ORCL": { region: "United States", name: "Oracle" },
  "PYPL": { region: "United States", name: "PayPal" },
  "AMD": { region: "United States", name: "Advanced Micro Devices" },

  // Europe / UK
  "NESN.SW": { region: "Europe / UK", name: "Nestlé" },
  "SIE.DE": { region: "Europe / UK", name: "Siemens" },
  "AIR.PA": { region: "Europe / UK", name: "Airbus" },
  "SAP.DE": { region: "Europe / UK", name: "SAP" },
  "MC.PA": { region: "Europe / UK", name: "LVMH" },
  "ASML.AS": { region: "Europe / UK", name: "ASML" },
  "RDSA.AS": { region: "Europe / UK", name: "Shell" },
  "ULVR.L": { region: "Europe / UK", name: "Unilever" },
  "HSBA.L": { region: "Europe / UK", name: "HSBC" },
  "BP.L": { region: "Europe / UK", name: "BP" },

  // Asia ex-India
  "0700.HK": { region: "Asia ex-India", name: "Tencent" },
  "9988.HK": { region: "Asia ex-India", name: "Alibaba Group" },
  "7203.T": { region: "Asia ex-India", name: "Toyota" },
  "6758.T": { region: "Asia ex-India", name: "Sony" },
  "005930.KS": { region: "Asia ex-India", name: "Samsung Electronics" },

  // Crypto / FX
  "BTC-USD": { region: "Crypto / FX", name: "Bitcoin" },
  "ETH-USD": { region: "Crypto / FX", name: "Ethereum" },
  "SOL-USD": { region: "Crypto / FX", name: "Solana" },
  "BNB-USD": { region: "Crypto / FX", name: "BNB" },
  "XRP-USD": { region: "Crypto / FX", name: "XRP" },
  "USDINR=X": { region: "Crypto / FX", name: "USD / INR" },
  "EURUSD=X": { region: "Crypto / FX", name: "EUR / USD" },
  "GBPUSD=X": { region: "Crypto / FX", name: "GBP / USD" },
};

const REGION_ORDER = [
  "India",
  "United States",
  "Europe / UK",
  "Asia ex-India",
  "Crypto / FX",
  "Others",
];

// DOM elements
const symbolsListEl = document.getElementById("symbols-list");
const lastUpdatedEl = document.getElementById("last-updated");
const detailSymbolEl = document.getElementById("detail-symbol");
const detailNameEl = document.getElementById("detail-name");
const detailRegionEl = document.getElementById("detail-region");
const detailDateEl = document.getElementById("detail-date");
const statCloseEl = document.getElementById("stat-close");
const statChangeAbsEl = document.getElementById("stat-change-abs");
const statChangePctEl = document.getElementById("stat-change-pct");
const insightContentEl = document.getElementById("insight-content");
const liveStatusTextEl = document.getElementById("live-status-text");
const refreshIntervalSelect = document.getElementById("refresh-interval");
const manualRefreshBtn = document.getElementById("manual-refresh");
const regionFilterSelect = document.getElementById("region-filter");

function formatNumber(n, decimals = 2) {
  const value = Number(n);
  if (Number.isNaN(value)) return "—";
  return value.toFixed(decimals);
}

function formatChange(change) {
  const value = Number(change);
  if (Number.isNaN(value)) return { text: "—", className: "change-flat" };
  if (value > 0) return { text: `+${value.toFixed(2)}`, className: "change-pos" };
  if (value < 0) return { text: value.toFixed(2), className: "change-neg" };
  return { text: value.toFixed(2), className: "change-flat" };
}

function formatChangePct(changePct) {
  const value = Number(changePct);
  if (Number.isNaN(value)) return { text: "—", className: "change-flat" };
  if (value > 0)
    return { text: `+${value.toFixed(2)}%`, className: "change-pos" };
  if (value < 0)
    return { text: `${value.toFixed(2)}%`, className: "change-neg" };
  return { text: `${value.toFixed(2)}%`, className: "change-flat" };
}

function clearSymbolsList() {
  symbolsListEl.innerHTML = "";
}

function renderSymbolsList(data) {
  clearSymbolsList();

  if (!Array.isArray(data) || data.length === 0) {
    symbolsListEl.innerHTML =
      '<p class="meta-text">No market data available yet. Start the backend streaming pipeline.</p>';
    return;
  }

  const selectedRegion = regionFilterSelect.value || "all";

  // Group by region
  const byRegion = {};
  for (const item of data) {
    const symbol = item.symbol || "N/A";
    const meta = SYMBOL_META[symbol];
    const region = meta?.region || "Others";

    if (selectedRegion !== "all" && region !== selectedRegion) {
      continue;
    }

    if (!byRegion[region]) byRegion[region] = [];
    byRegion[region].push(item);
  }

  let anyRendered = false;

  REGION_ORDER.forEach((region) => {
    const items = byRegion[region];
    if (!items || items.length === 0) return;

    anyRendered = true;

    const sectionEl = document.createElement("div");
    sectionEl.className = "symbol-section";

    const titleEl = document.createElement("div");
    titleEl.className = "symbol-section-title";
    titleEl.textContent = region;
    sectionEl.appendChild(titleEl);

    // Sort by symbol
    items.sort((a, b) =>
      (a.symbol || "").localeCompare(b.symbol || "")
    );

    items.forEach((item) => {
      const symbol = item.symbol || "N/A";
      const meta = SYMBOL_META[symbol];
      const name = meta?.name || "Streaming instrument";
      const close = Number(item.close_price);
      const changeAbs = Number(item.change_abs);
      const changePct = Number(item.change_pct);

      const changeObj = formatChange(changeAbs);
      const changePctObj = formatChangePct(changePct);

      const row = document.createElement("div");
      row.className = "symbol-item";
      row.dataset.symbol = symbol;

      if (symbol === activeSymbol) {
        row.classList.add("symbol-item--active");
      }

      row.innerHTML = `
        <div class="symbol-main">
          <span class="symbol-code">${symbol}</span>
          <span class="symbol-label">${name}</span>
        </div>
        <div class="symbol-price">
          ${Number.isNaN(close) ? "—" : formatNumber(close, 2)}
        </div>
        <div class="symbol-change">
          <span class="${changeObj.className}">${changeObj.text}</span>
          <span style="margin-left:4px" class="${changePctObj.className}">
            ${changePctObj.text}
          </span>
        </div>
      `;

      row.addEventListener("click", () => {
        activeSymbol = symbol;
        updateDetailPanel(item);
        highlightActiveSymbol();
      });

      sectionEl.appendChild(row);
    });

    symbolsListEl.appendChild(sectionEl);
  });

  if (!anyRendered) {
    symbolsListEl.innerHTML =
      '<p class="meta-text">No instruments for this region in the latest snapshot.</p>';
  }
}

function highlightActiveSymbol() {
  const items = symbolsListEl.querySelectorAll(".symbol-item");
  items.forEach((el) => {
    if (el.dataset.symbol === activeSymbol) {
      el.classList.add("symbol-item--active");
    } else {
      el.classList.remove("symbol-item--active");
    }
  });
}

function updateDetailPanel(item) {
  if (!item) {
    detailSymbolEl.textContent = "Select an instrument";
    detailNameEl.textContent =
      "Click any row in the watchlist to view structured analytics.";
    detailRegionEl.textContent = "Region —";
    detailDateEl.textContent = "—";
    statCloseEl.textContent = "—";
    statChangeAbsEl.textContent = "—";
    statChangePctEl.textContent = "—";
    insightContentEl.innerHTML =
      '<p class="ai-placeholder">Select any symbol in the global watchlist to view an English, human-readable explanation of what is happening in that market.</p>';
    return;
  }

  const symbol = item.symbol || "N/A";
  const meta = SYMBOL_META[symbol];
  const region = meta?.region || "Others";
  const name = meta?.name || "Streaming instrument";

  detailSymbolEl.textContent = symbol;
  detailNameEl.textContent = name;
  detailRegionEl.textContent = `Region — ${region}`;
  detailDateEl.textContent = item.date || "—";

  const close = Number(item.close_price);
  statCloseEl.textContent = formatNumber(close, 2);

  const changeObj = formatChange(Number(item.change_abs));
  statChangeAbsEl.textContent = changeObj.text;
  statChangeAbsEl.className = "metric-value " + changeObj.className;

  const changePctObj = formatChangePct(Number(item.change_pct));
  statChangePctEl.textContent = changePctObj.text;
  statChangePctEl.className = "metric-value " + changePctObj.className;

  const insight =
    item.insight && item.insight.trim().length > 0
      ? item.insight
      : "No AI insight available for this symbol in the latest snapshot.";
  insightContentEl.textContent = insight;
}

async function fetchLatestInsights() {
  try {
    liveStatusTextEl.textContent = "Syncing…";

    const res = await fetch(`${API_BASE}/api/market/latest`);
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }
    const data = await res.json();
    currentData = Array.isArray(data) ? data : [];

    renderSymbolsList(currentData);

    if (!activeSymbol && currentData.length > 0) {
      activeSymbol = currentData[0].symbol;
    }

    const activeItem = currentData.find((x) => x.symbol === activeSymbol);
    updateDetailPanel(activeItem);

    highlightActiveSymbol();

    const now = new Date();
    lastUpdatedEl.textContent = `Last updated — ${now.toLocaleTimeString()}`;
    liveStatusTextEl.textContent = "Live stream";
  } catch (err) {
    console.error("Failed to fetch insights:", err);
    liveStatusTextEl.textContent = "Offline";
    lastUpdatedEl.textContent =
      "Last updated — error fetching data from backend";
    symbolsListEl.innerHTML =
      '<p class="meta-text">Unable to reach backend API. Is the FastAPI server running on port 8000?</p>';
  }
}

function startAutoRefresh() {
  if (refreshTimer) clearInterval(refreshTimer);
  const seconds = Number(refreshIntervalSelect.value || "10");
  refreshTimer = setInterval(fetchLatestInsights, seconds * 1000);
}

// ---- Bootstrap ----
document.addEventListener("DOMContentLoaded", () => {
  fetchLatestInsights();
  startAutoRefresh();

  refreshIntervalSelect.addEventListener("change", () => {
    startAutoRefresh();
  });

  manualRefreshBtn.addEventListener("click", () => {
    fetchLatestInsights();
  });

  regionFilterSelect.addEventListener("change", () => {
    renderSymbolsList(currentData);
    const activeItem = currentData.find((x) => x.symbol === activeSymbol);
    updateDetailPanel(activeItem);
    highlightActiveSymbol();
  });
});
