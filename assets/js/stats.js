async function loadData() {
  const res = await fetch("data/prices.json");
  return await res.json();
}

function formatNumber(x) {
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 2 }).format(x);
}

function buildPlots(rows) {
  const dates = rows.map(r => r.date);
  const btc = rows.map(r => r.btc_close);
  const eth = rows.map(r => r.eth_close);

  const btcPct = rows.map(r => r.btc_pct);
  const ethPct = rows.map(r => r.eth_pct);

  Plotly.newPlot("pricePlot", [
    { x: dates, y: btc, type: "scatter", mode: "lines", name: "BTC" },
    { x: dates, y: eth, type: "scatter", mode: "lines", name: "ETH" }
  ], { title: "Prix BTC & ETH (USD)" });

  Plotly.newPlot("changePlot", [
    { x: dates, y: btcPct, type: "scatter", mode: "lines", name: "BTC %" },
    { x: dates, y: ethPct, type: "scatter", mode: "lines", name: "ETH %" }
  ], { title: "Variations journalières (%)" });
}

function buildTable(rows, tableId = "#cryptoTable") {
  const tbody = document.querySelector(`${tableId} tbody`);
  tbody.innerHTML = "";

  rows.slice().reverse().forEach(r => {
    tbody.innerHTML += `
      <tr>
        <td>${r.date}</td>
        <td>${formatNumber(r.btc_close ?? r.btc_pred)}</td>
        <td>${formatNumber(r.eth_close ?? r.eth_pred)}</td>
        <td>${r.btc_pct !== undefined ? formatNumber(r.btc_pct) + "%" : ""}</td>
        <td>${r.eth_pct !== undefined ? formatNumber(r.eth_pct) + "%" : ""}</td>
      </tr>
    `;
  });

  if ($.fn.DataTable.isDataTable(tableId)) {
    $(tableId).DataTable().clear().destroy();
  }

  new DataTable(tableId, {
    pageLength: 25,
    order: [[0, "desc"]]
  });
}

async function buildPredictions() {
  const res = await fetch("data/predictions.json");
  const rows = await res.json();

  const dates = rows.map(r => r.date);
  const btc = rows.map(r => r.btc_pred);
  const eth = rows.map(r => r.eth_pred);

  Plotly.newPlot("predictionPlot", [
    { x: dates, y: btc, type: "scatter", mode: "lines+markers", name: "BTC prédiction" },
    { x: dates, y: eth, type: "scatter", mode: "lines+markers", name: "ETH prédiction" }
  ], { title: "Prédictions BTC & ETH" });

  // Mise à jour de la table de prédictions
  buildTable(rows, "#predictionTable");
}

// -------------------------
// Main : ne l'appelle qu'une seule fois
// -------------------------
(async function main() {
  const rows = await loadData();
  buildPlots(rows);
  buildTable(rows); // Table historique
  await buildPredictions(); // Table de prédictions + plot
})();
