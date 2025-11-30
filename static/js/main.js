let map;
let graphLayer;        
let islandsLayer;      
let mstLayer;          
let propagationLayer;  
let nodeMarkers = {};  
let lastGraphData = null; 

const POLLUTANT_THRESHOLDS = {
  PM2_5: {
    label: "PM\u2082.\u2085",
    unit: "µg/m³",
    rows: [
      { level: "Buena",              oms: "0–15",   minam: "0–25",   colorClass: "green",  colorLabel: "Verde" },
      { level: "Moderada",           oms: "15–35",  minam: "25–50",  colorClass: "yellow", colorLabel: "Amarillo" },
      { level: "Dañina (sensible)",  oms: "35–55",  minam: "50–75",  colorClass: "orange", colorLabel: "Naranja" },
      { level: "Dañina (general)",   oms: "55–150", minam: "75–125", colorClass: "red",    colorLabel: "Rojo" },
      { level: "Peligrosa",          oms: ">150",   minam: ">125",   colorClass: "purple", colorLabel: "Morado" }
    ]
  },
  PM10: {
    label: "PM\u2081\u2080",
    unit: "µg/m³",
    rows: [
      { level: "Buena",              oms: "0–45",   minam: "0–50",   colorClass: "green",  colorLabel: "Verde" },
      { level: "Moderada",           oms: "45–75",  minam: "50–100", colorClass: "yellow", colorLabel: "Amarillo" },
      { level: "Dañina (sensible)",  oms: "75–125", minam: "100–150",colorClass: "orange", colorLabel: "Naranja" },
      { level: "Dañina (general)",   oms: "125–250",minam: "150–300",colorClass: "red",    colorLabel: "Rojo" },
      { level: "Peligrosa",          oms: ">250",   minam: ">300",   colorClass: "purple", colorLabel: "Morado" }
    ]
  },
  NO2: {
    label: "NO\u2082",
    unit: "µg/m³",
    rows: [
      { level: "Buena",              oms: "0–25",   minam: "0–100",  colorClass: "green",  colorLabel: "Verde" },
      { level: "Moderada",           oms: "25–50",  minam: "100–200",colorClass: "yellow", colorLabel: "Amarillo" },
      { level: "Dañina (sensible)",  oms: "50–100", minam: "200–300",colorClass: "orange", colorLabel: "Naranja" },
      { level: "Dañina (general)",   oms: "100–200",minam: "300–500",colorClass: "red",    colorLabel: "Rojo" },
      { level: "Peligrosa",          oms: ">200",   minam: ">500",   colorClass: "purple", colorLabel: "Morado" }
    ]
  },
  AVG: {
    label: "Promedio (AVG)",
    unit: "µg/m³ (promedio de PM\u2082.\u2085, PM\u2081\u2080 y NO\u2082)",
    rows: [
      { level: "Buena",              oms: "0–28",   minam: "0–60",   colorClass: "green",  colorLabel: "Verde" },
      { level: "Moderada",           oms: "28–53",  minam: "60–115", colorClass: "yellow", colorLabel: "Amarillo" },
      { level: "Dañina (sensible)",  oms: "53–93",  minam: "115–175",colorClass: "orange", colorLabel: "Naranja" },
      { level: "Dañina (general)",   oms: "93–200", minam: "175–300",colorClass: "red",    colorLabel: "Rojo" },
      { level: "Peligrosa",          oms: ">200",   minam: ">300",   colorClass: "purple", colorLabel: "Morado" }
    ]
  }
};

let currentGraphRequestId = 0;
document.addEventListener("DOMContentLoaded", () => {
  initMap();
  initUI();
  loadInitialGraph();
});

function initMap() {
  map = L.map("map").setView([-12.05, -77.04], 11);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: '© OpenStreetMap'
}).addTo(map);

  graphLayer = L.layerGroup().addTo(map);
  islandsLayer = L.layerGroup().addTo(map);
  mstLayer = L.layerGroup().addTo(map);
  propagationLayer = L.layerGroup().addTo(map);
}

function initUI() {
  const thRange = document.getElementById("th-range");
  const thValue = document.getElementById("th-value");

  if (thRange && thValue) {
    thValue.textContent = thRange.value;
    thRange.addEventListener("input", () => {
      thValue.textContent = thRange.value;
    });
  }

  const filtersForm = document.getElementById("filters-form");
  if (filtersForm) {
    filtersForm.addEventListener("submit", (e) => {
      e.preventDefault();
      fetchAndRenderGraph();
    });
  }

  const btnBfs = document.getElementById("btn-bfs");
  if (btnBfs) {
    btnBfs.addEventListener("click", handleBfsIslands);
  }

  const btnUfds = document.getElementById("btn-ufds");
  if (btnUfds) {
    btnUfds.addEventListener("click", handleUfdsCommunities);
  }

  const btnMst = document.getElementById("btn-mst");
  if (btnMst) {
    btnMst.addEventListener("click", handleMst);
  }

  const btnPropagation = document.getElementById("btn-propagation");
  if (btnPropagation) {
    btnPropagation.addEventListener("click", handlePropagation);
  }

  const pollutantSelect = document.getElementById("pollutant-select");
  if (pollutantSelect) {
    pollutantSelect.addEventListener("change", () => {
      showThresholdsFromUI();
    });
  }

  const modeRadios = document.querySelectorAll("input[name='mode']");
  modeRadios.forEach((radio) => {
    radio.addEventListener("change", () => {
      showThresholdsFromUI();

    });
  });

  const dateInput = document.getElementById("date-input");
  if (dateInput && dateInput.showPicker) {
    dateInput.addEventListener("click", () => dateInput.showPicker());
    dateInput.addEventListener("focus", () => dateInput.showPicker());
  }
}

async function loadInitialGraph() {
  try {
    const requestId = ++currentGraphRequestId;

    const res = await fetch("/api/graph");
    if (!res.ok) throw new Error("Error al llamar /api/graph");

    const data = await res.json();

    if (requestId !== currentGraphRequestId) {
      console.warn("Respuesta inicial descartada por estar desactualizada");
      return;
    }

    const dateInput = document.getElementById("date-input");
    if (dateInput && data.date) {
      dateInput.value = data.date;
    }

    renderGraph(data);
  } catch (err) {
    console.error(err);
    showError("No se pudo cargar el grafo inicial.");
  }
}


async function fetchAndRenderGraph() {
  clearAlgorithmLayers();

  const date = document.getElementById("date-input").value;
  const pollutant = document.getElementById("pollutant-select").value;
  const mode =
    document.querySelector("input[name='mode']:checked")?.value || "OMS";
  const th = document.getElementById("th-range").value;

  const params = new URLSearchParams();
  if (date) params.append("date", date);
  params.append("pollutant", pollutant);
  params.append("mode", mode);
  params.append("th", th);

  // NUEVO: id para esta petición
  const requestId = ++currentGraphRequestId;

  try {
    const res = await fetch(`/api/graph?${params.toString()}`);
    if (!res.ok) throw new Error("Error al actualizar grafo");

    const data = await res.json();

    if (requestId !== currentGraphRequestId) {
      console.warn("Respuesta de /api/graph descartada por estar desactualizada");
      return;
    }

    renderGraph(data);
  } catch (err) {
    console.error(err);
    showError("No se pudo actualizar el grafo con los filtros seleccionados.");
  }
}


function renderGraph(data) {
  lastGraphData = data;

  graphLayer.clearLayers();
  clearAlgorithmLayers();     
  nodeMarkers = {};

  if (!data || !data.nodes || data.nodes.length === 0) {
    showError("No hay nodos para la fecha y parámetros seleccionados.");
    updateGraphSummary(null);
    return;
  }

  const markers = [];
  data.nodes.forEach((node) => {
    const lat = node.latitud;
    const lon = node.longitud;
    if (lat == null || lon == null) return;

    const color = mapColor(node.color);

    const marker = L.circleMarker([lat, lon], {
      radius: 8,
      color: "#000000",
      weight: 1,
      fillColor: color,
      fillOpacity: 0.9
    });

    const popupHtml = `
      <div class="small">
        <strong>${node.distrito}</strong><br/>
        Fecha: ${node.fecha}<br/>
        PM2.5: ${node.pm2_5} <br/>
        PM10: ${node.pm10} <br/>
        NO₂: ${node.no2} <br/>
        AVG: ${node.avg} <br/>
        Color: <span style="color:${color}; font-weight:bold;">${node.color}</span>
      </div>
    `;


    marker.bindPopup(popupHtml);
    marker.addTo(graphLayer);

    nodeMarkers[node.id] = marker;
    markers.push(marker);
  });

if (Array.isArray(data.edges)) {
  data.edges.forEach((edge) => {
    const srcMarker = nodeMarkers[edge.source];
    const dstMarker = nodeMarkers[edge.destination];
    if (!srcMarker || !dstMarker) return;

    const latlngs = [srcMarker.getLatLng(), dstMarker.getLatLng()];

    const polyline = L.polyline(latlngs, {
      color: "#666666",
      weight: 2.5,  
      opacity: 0.6
    }).addTo(graphLayer);

    if (edge.distance != null) {
      const distKm = Number(edge.distance).toFixed(2);

      polyline.bindTooltip(
        `Distancia: ${distKm} km`,
        {
          sticky: true,          
          direction: "center",   
          className: "edge-tooltip"
        }
      );
    }
  });
}


  const group = L.featureGroup(Object.values(nodeMarkers));
  map.fitBounds(group.getBounds().pad(0.2));

  updateGraphSummary(data);
  setAlgoSummary(
    "Grafo actualizado.",
    "Puedes ejecutar ahora BFS, UFDS, MST o propagación usando los botones de la izquierda."
  );
}

function mapColor(colorName) {
  const c = (colorName || "").toLowerCase();
  switch (c) {
    case "green":
      return "#2ecc71";
    case "yellow":
      return "#f1c40f";
    case "orange":
      return "#e67e22";
    case "red":
      return "#e74c3c";
    case "purple":
      return "#8e44ad";
    default:
      return "#95a5a6";
  }
}

function updateGraphSummary(data) {
  const dateSpan = document.getElementById("info-date");
  const pollutantSpan = document.getElementById("info-pollutant");
  const modeSpan = document.getElementById("info-mode");
  const nodesSpan = document.getElementById("info-nodes");
  const edgesSpan = document.getElementById("info-edges");

  if (!data) {
    if (dateSpan) dateSpan.textContent = "–";
    if (pollutantSpan) pollutantSpan.textContent = "–";
    if (modeSpan) modeSpan.textContent = "–";
    if (nodesSpan) nodesSpan.textContent = "–";
    if (edgesSpan) edgesSpan.textContent = "–";
    return;
  }

  if (dateSpan) dateSpan.textContent = data.date || "–";
  if (pollutantSpan) pollutantSpan.textContent = data.pollutant || "–";
  if (modeSpan) modeSpan.textContent = data.mode || "–";
  if (nodesSpan) nodesSpan.textContent = data.nodes?.length ?? "–";
  if (edgesSpan) edgesSpan.textContent = data.edges?.length ?? "–";
}


function showPollutantThresholds(pollutantKey) {
  const info = POLLUTANT_THRESHOLDS[pollutantKey];
  if (!info) return;

  const mode =
    document.querySelector("input[name='mode']:checked")?.value || "OMS";
  const isOms = mode === "OMS";
  const rangoColTitle = isOms ? "Rango OMS" : "Rango MINAM";

  const title = `Umbrales de ${info.label} (${mode})`;

  let rowsHtml = "";
  info.rows.forEach((row) => {
    const rango = isOms ? row.oms : row.minam;
    rowsHtml += `
      <tr>
        <td>${row.level}</td>
        <td>${rango}</td>
        <td>
          <span class="legend legend-${row.colorClass} me-1"></span>
          ${row.colorLabel}
        </td>
      </tr>
    `;
  });

  const tableHtml = `
    <p class="mb-2 small">
      Clasificación de niveles para <strong>${info.label}</strong> (${info.unit}).<br>
      Modo de umbrales actual: <strong>${mode}</strong>.
    </p>
    <table class="table table-sm table-dark table-borderless mb-0 align-middle">
      <thead class="small">
        <tr>
          <th>Nivel</th>
          <th>${rangoColTitle}</th>
          <th>Color</th>
        </tr>
      </thead>
      <tbody class="small">
        ${rowsHtml}
      </tbody>
    </table>
  `;

  setAlgoSummary(title, tableHtml);
}


function showThresholdsFromUI() {
  const pollutant = document.getElementById("pollutant-select")?.value;
  if (!pollutant) return;
  showPollutantThresholds(pollutant);
}

function setAlgoSummary(mainText, extraHtml) {
  const main = document.getElementById("algo-summary-main");
  const extra = document.getElementById("algo-extra-info");
  if (main) main.textContent = mainText || "";
  if (extra) extra.innerHTML = extraHtml || "";
}

function syncGraphSummaryFromUI() {
  const pollutantSelect = document.getElementById("pollutant-select");
  const modeRadio = document.querySelector("input[name='mode']:checked");

  const pollutantSpan = document.getElementById("info-pollutant");
  const modeSpan = document.getElementById("info-mode");

  if (!pollutantSelect || !modeRadio || !pollutantSpan || !modeSpan) return;

  const label = pollutantSelect.options[pollutantSelect.selectedIndex].textContent.trim();
  const modeLabel = modeRadio.value || "–";

  pollutantSpan.textContent = label || "–";
  modeSpan.textContent = modeLabel;
}

function showError(msg) {
  setAlgoSummary("Error", `<span class="text-danger">${msg}</span>`);
}

function clearAlgorithmLayers() {
  islandsLayer.clearLayers();
  mstLayer.clearLayers();
  propagationLayer.clearLayers();
  const bfsBadge = document.getElementById("bfs-count-badge");
  const ufdsBadge = document.getElementById("ufds-count-badge");
  const mstBadge = document.getElementById("mst-count-badge");
  if (bfsBadge) bfsBadge.textContent = "–";
  if (ufdsBadge) ufdsBadge.textContent = "–";
  if (mstBadge) mstBadge.textContent = "–";
}

async function handleBfsIslands() {
  if (!lastGraphData) {
    showError("Primero carga un grafo con los filtros.");
    return;
  }

  islandsLayer.clearLayers();

  const date = document.getElementById("date-input").value || lastGraphData.date;
  const pollutant = document.getElementById("pollutant-select").value;
  const mode =
    document.querySelector("input[name='mode']:checked")?.value || "OMS";
  const th = document.getElementById("th-range").value;
  const severity = document.getElementById("severity-select").value;

  const params = new URLSearchParams();
  if (date) params.append("date", date);
  params.append("pollutant", pollutant);
  params.append("mode", mode);
  params.append("th", th);
  params.append("severity", severity);

  try {
    const res = await fetch(`/api/islas?${params.toString()}`);
    if (!res.ok) throw new Error("Error en /api/islas");

    const data = await res.json();
    const islands = data.islands || [];

    const bfsBadge = document.getElementById("bfs-count-badge");
    if (bfsBadge) bfsBadge.textContent = islands.length;

    const highlightColors = ["#ffffff", "#00e5ff", "#ff00ff", "#00ff7f", "#ffea00"];

    islands.forEach((island, idx) => {
      const highlightColor =
        highlightColors[idx % highlightColors.length] || "#ffffff";

      island.forEach((nodeId) => {
        const baseMarker = nodeMarkers[nodeId];
        if (!baseMarker) return;
        const latlng = baseMarker.getLatLng();

        L.circleMarker(latlng, {
          radius: 13,              
          color: "#000000",       
          weight: 3,
          fillColor: highlightColor,
          fillOpacity: 0.45,       
          opacity: 1
        }).addTo(islandsLayer);
      });
    });


    const extraHtml = `
      <p class="mb-1">
        <strong>BFS</strong> detectó <strong>${islands.length}</strong> islas de contaminación
        con severidad mínima <strong>${severity}</strong> (${mode}) para el contaminante
        <strong>${pollutant}</strong>.
      </p>
      ${
        islands.length > 0
          ? `<p class="mb-0 small text-secondary">Cada isla se resalta con un aro de color en el mapa.</p>`
          : `<p class="mb-0 small text-secondary">No se encontraron islas que cumplan con la severidad seleccionada.</p>`
      }
    `;
    setAlgoSummary("Islas de contaminación (BFS)", extraHtml);
  } catch (err) {
    console.error(err);
    showError("No se pudo ejecutar BFS / islas.");
  }
}

async function handleUfdsCommunities() {
  if (!lastGraphData) {
    showError("Primero carga un grafo con los filtros.");
    return;
  }

  const date = document.getElementById("date-input").value || lastGraphData.date;
  const pollutant = document.getElementById("pollutant-select").value;
  const mode =
    document.querySelector("input[name='mode']:checked")?.value || "OMS";
  const th = document.getElementById("th-range").value;

  const params = new URLSearchParams();
  if (date) params.append("date", date);
  params.append("pollutant", pollutant);
  params.append("mode", mode);
  params.append("th", th);

  try {
    const res = await fetch(`/api/communities?${params.toString()}`);
    if (!res.ok) throw new Error("Error en /api/communities");

    const data = await res.json();
    const communities = data.communities || [];

    const ufdsBadge = document.getElementById("ufds-count-badge");
    if (ufdsBadge) ufdsBadge.textContent = communities.length;

    communities.sort((a, b) => (b.nodes?.length || 0) - (a.nodes?.length || 0));

    let html = "<ul class='mb-1'>";
    communities.slice(0, 5).forEach((c) => {
      html += `<li>Color <strong>${c.color}</strong>: ${c.nodes.length} nodos</li>`;
    });
    html += "</ul>";

    const extraHtml = `
      <p class="mb-1">
        <strong>UFDS</strong> detectó <strong>${communities.length}</strong> comunidades agrupando
        distritos por color (nivel de contaminación) usando <strong>${pollutant}</strong> y modo <strong>${mode}</strong>.
      </p>
      ${html}
      <p class="mb-0 small text-secondary">
        Las comunidades no dependen de la conectividad geográfica, sino del nivel de contaminación.
      </p>
    `;
    setAlgoSummary("Comunidades por color (UFDS)", extraHtml);
  } catch (err) {
    console.error(err);
    showError("No se pudo ejecutar UFDS / communities.");
  }
}

async function handleMst() {
  if (!lastGraphData) {
    showError("Primero carga un grafo con los filtros.");
    return;
  }

  mstLayer.clearLayers();

  const date = document.getElementById("date-input").value || lastGraphData.date;

  const params = new URLSearchParams();
  if (date) params.append("date", date);

  try {
    const res = await fetch(`/api/mst?${params.toString()}`);
    if (!res.ok) throw new Error("Error en /api/mst");

    const data = await res.json();
    const edges = data.edges || [];

    const mstBadge = document.getElementById("mst-count-badge");
    if (mstBadge) mstBadge.textContent = data.mst_edge_count ?? edges.length;

    if (graphLayer && nodeMarkers) {
      graphLayer.clearLayers(); 
      Object.values(nodeMarkers).forEach((marker) => {
        marker.addTo(graphLayer);
      });
    }

    edges.forEach((edge) => {
      const srcMarker = nodeMarkers[edge.source];
      const dstMarker = nodeMarkers[edge.destination];
      if (!srcMarker || !dstMarker) return;

      const latlngs = [srcMarker.getLatLng(), dstMarker.getLatLng()];
      const poly = L.polyline(latlngs, {
        color: "#00ff7f",
        weight: 3,
        opacity: 0.9
      }).addTo(mstLayer);

      if (edge.distance !== undefined) {
        poly.bindTooltip(`Distancia: ${edge.distance} km`, {
          sticky: true,
          direction: "center",
          className: "mst-tooltip"
        });
      }
    });

    const extraHtml = `
      <p class="mb-1">
        El MST conecta <strong>${data.node_count}</strong> nodos con
        <strong>${data.mst_edge_count}</strong> aristas, minimizando la suma de distancias.
      </p>
      <p class="mb-1 small">
        <strong>Peso total:</strong> ${data.total_weight} km · Umbral base: ${data.threshold} km.
      </p>
      <p class="mb-0 small text-secondary">
        Las aristas del MST se muestran en verde brillante y muestran la distancia al pasar el cursor.
      </p>
    `;
    setAlgoSummary("Árbol de expansión mínima (Kruskal)", extraHtml);
  } catch (err) {
    console.error(err);
    showError("No se pudo calcular el MST.");
  }
}

async function handlePropagation() {
  if (!lastGraphData) {
    showError("Primero carga un grafo con los filtros.");
    return;
  }

  propagationLayer.clearLayers();

  const date = document.getElementById("date-input").value || lastGraphData.date;

  const originSelect = document.getElementById("origin-select");
  const origin = originSelect && originSelect.value
    ? originSelect.value.trim()
    : "";

  console.log("Origen seleccionado:", origin);

  if (!origin) {
    showError("Selecciona un distrito de origen para la propagación.");
    return;
  }

  const params = new URLSearchParams();
  params.append("origin", origin);
  if (date) params.append("date", date);

  try {
    const res = await fetch(`/api/propagation?${params.toString()}`);
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      let msg = "Error en /api/propagation.";
      if (errData.error) {
        msg += " " + errData.error;
      }
      throw new Error(msg);
    }

    const data = await res.json();
    const order = data.order || [];
    const distances = data.distances || {};

    let html = "<ol class='mb-1 small'>";
    order.forEach((nodeId) => {
      const dist = distances[nodeId]?.toFixed
        ? distances[nodeId].toFixed(2)
        : distances[nodeId];
      const niceName = formatNodeId(nodeId);
      html += `<li>${niceName} <span class="text-secondary">(dist: ${dist} km)</span></li>`;
    });
    html += "</ol>";

    const extraHtml = `
      <p class="mb-1">
        <strong>Dijkstra</strong> calculó la distancia mínima desde el origen
        <strong>${formatNodeId(data.origin || "")}</strong> hacia todos los distritos
        del grafo del día <strong>${data.date}</strong>.
      </p>
      ${html}
      <p class="mb-0 small text-secondary">
        En el mapa, la propagación se anima con círculos turquesa siguiendo el orden calculado.
      </p>
    `;
    setAlgoSummary("Propagación desde un distrito (Dijkstra)", extraHtml);

    animatePropagation(order);
  } catch (err) {
    console.error(err);
    showError(err.message || "No se pudo ejecutar la propagación.");
  }
}


function animatePropagation(order) {
  propagationLayer.clearLayers();
  const delayPerNode = 700; // ms

  order.forEach((nodeId, index) => {
    setTimeout(() => {
      const marker = nodeMarkers[nodeId];
      if (!marker) return;
      const latlng = marker.getLatLng();

      const circle = L.circle(latlng, {
        radius: 800,          // más grande para que se note
        color: "#ffffff",     // borde blanco bien visible
        weight: 3,            // línea más gruesa
        fillColor: "#00b0ff", // azul intenso
        fillOpacity: 0.4      // más opaco para que destaque
      }).addTo(propagationLayer);

      setTimeout(() => {
        propagationLayer.removeLayer(circle);
      }, delayPerNode * 3);
    }, index * delayPerNode);
  });
}


function formatNodeId(nodeId) {
  if (!nodeId || typeof nodeId !== "string") return nodeId;
  const parts = nodeId.split("_");
  if (parts.length < 2) return nodeId;
  const date = parts[parts.length - 1];
  const districtParts = parts.slice(0, -1);
  const district = districtParts
    .map((p) => p.charAt(0) + p.slice(1).toLowerCase())
    .join(" ");
  return `${district} (${date})`;
}
