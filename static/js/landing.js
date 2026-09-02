```
document.addEventListener("DOMContentLoaded", () => {
  initMobileMenu();
  initSmoothScrolling();
  initNigeriaMap();
});

function initMobileMenu() {
  const header = document.querySelector(".site-header");
  const button = document.querySelector(".mobile-menu");

  if (!header || !button) return;

  button.addEventListener("click", () => {
    const open = header.classList.toggle("menu-open");
    button.classList.toggle("active", open);
    button.setAttribute("aria-expanded", String(open));
  });

  header.querySelectorAll(".nav-links a, .nav-actions a").forEach(link => {
    link.addEventListener("click", () => {
      header.classList.remove("menu-open");
      button.classList.remove("active");
      button.setAttribute("aria-expanded", "false");
    });
  });
}

function initSmoothScrolling() {
  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener("click", event => {
      const target = document.querySelector(link.getAttribute("href"));

      if (!target) return;

      event.preventDefault();
      target.scrollIntoView({
        behavior: "smooth",
        block: "start"
      });
    });
  });
}

async function initNigeriaMap() {
  const map = document.querySelector(".nigeria-map");

  if (!map) return;

  const geojsonUrl = map.dataset.geojsonUrl;

  if (!geojsonUrl) {
    showMapError(map, "Map data is unavailable.");
    return;
  }

  try {
    const response = await fetch(geojsonUrl);

    if (!response.ok) {
      throw new Error(`Map request failed: ${response.status}`);
    }

    const geojson = await response.json();

    if (
      geojson?.type !== "FeatureCollection" ||
      !Array.isArray(geojson.features)
    ) {
      throw new Error("Invalid GeoJSON data.");
    }

    renderNigeriaMap(map, geojson);
  } catch (error) {
    console.error("Nigeria map error:", error);
    showMapError(map, "Unable to load the Nigeria state map.");
  }
}

function renderNigeriaMap(container, geojson) {
  const states = geojson.features.filter(feature =>
    feature?.geometry &&
    ["Polygon", "MultiPolygon"].includes(feature.geometry.type)
  );

  if (!states.length) {
    showMapError(container, "No state boundaries were found.");
    return;
  }

  const width = 700;
  const height = 650;
  const bounds = getGeoBounds(states);
  const project = createProjection(bounds, width, height);

  const svg = createSvg("svg", {
    class: "nigeria-map-svg",
    viewBox: `0 0 ${width} ${height}`,
    role: "img",
    "aria-label": "Interactive map of Nigeria"
  });

  states.forEach((feature, index) => {
    const stateName = getStateName(feature);
    const pathData = geometryToPath(feature.geometry, project);

    if (!stateName || !pathData) return;

    const path = createSvg("path", {
      class: "geo-state",
      d: pathData,
      tabindex: "0",
      role: "button",
      "aria-label": stateName,
      "data-state": stateName
    });

    path.style.setProperty(
      "--map-delay",
      `${Math.min(index * 0.025, 0.8)}s`
    );

    path.addEventListener("mouseenter", event => {
      showMapTooltip(container, stateName, event);
    });

    path.addEventListener("mousemove", event => {
      moveMapTooltip(container, event);
    });

    path.addEventListener("mouseleave", () => {
      hideMapTooltip(container);
    });

    path.addEventListener("focus", () => {
      showMapTooltip(container, stateName);
    });

    path.addEventListener("blur", () => {
      hideMapTooltip(container);
    });

    path.addEventListener("click", () => {
      selectState(container, stateName, path);
    });

    path.addEventListener("keydown", event => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        selectState(container, stateName, path);
      }
    });

    svg.appendChild(path);
  });

  const oldSvg = container.querySelector(".nigeria-map-svg");

  if (oldSvg) {
    oldSvg.replaceWith(svg);
  } else {
    container.insertBefore(svg, container.firstChild);
  }

  let tooltip = container.querySelector(".map-tooltip");

  if (!tooltip) {
    tooltip = createMapTooltip();
    container.appendChild(tooltip);
  }

  if (!container._statePanel) {
    const panel = createStatePanel();
    const card = container.closest(".map-card");

    if (card) {
      card.appendChild(panel);
    } else {
      container.appendChild(panel);
    }

    container._statePanel = panel;
  }
}

function selectState(container, stateName, path) {
  container
    .querySelectorAll(".geo-state.selected")
    .forEach(state => state.classList.remove("selected"));

  path.classList.add("selected");
  hideMapTooltip(container);

  const panel = container._statePanel;

  if (!panel) return;

  panel.hidden = false;
  panel.innerHTML = `
    <div class="state-data-header">
      <div>
        <div class="state-data-label">State Overview</div>
        <div class="state-data-title">${escapeHtml(stateName)} State</div>
      </div>

      <button
        type="button"
        class="state-data-close"
        aria-label="Close state statistics"
      >×</button>
    </div>

    <div class="state-data-content">
      <div class="state-data-loading">
        <div>
          <div class="state-data-spinner"></div>
          Loading state statistics...
        </div>
      </div>
    </div>
  `;

  panel.querySelector(".state-data-close").addEventListener(
    "click",
    () => clearSelectedState(container)
  );

  loadStateStatistics(container, stateName);
}

async function loadStateStatistics(container, stateName) {
  const panel = container._statePanel;

  if (!panel) return;

  try {
    const response = await fetch(
      `/data/state-summary?state=${encodeURIComponent(stateName)}`
    );

    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }

    const data = await response.json();

    if (!data || data.state === undefined) {
      throw new Error("Invalid state statistics response.");
    }

    renderStateStatistics(panel, data);
  } catch (error) {
    console.error("State statistics error:", error);

    const content = panel.querySelector(".state-data-content");

    if (!content) return;

    content.innerHTML = `
      <div class="state-data-error">
        Unable to load statistics for
        <strong>${escapeHtml(stateName)} State</strong>.
        <br>
        <button type="button" class="state-data-retry">
          Try again
        </button>
      </div>
    `;

    content.querySelector(".state-data-retry").addEventListener(
      "click",
      () => loadStateStatistics(container, stateName)
    );
  }
}

function renderStateStatistics(panel, data) {
  const content = panel.querySelector(".state-data-content");

  if (!content) return;

  content.innerHTML = `
    <div class="state-data-grid">
      <div class="state-data-stat featured">
        <span>Observed VA Records</span>
        <strong>${formatNumber(data.observed_records)}</strong>
        <small>Records in the platform</small>
      </div>

      <div class="state-data-stat">
        <span>Estimated VA Burden</span>
        <strong>
          ${
            data.estimated_records == null
              ? "N/A"
              : formatNumber(data.estimated_records)
          }
        </strong>
        <small>
          ${escapeHtml(
            data.estimated_records_status ||
            "Validated estimate required"
          )}
        </small>
      </div>

      <div class="state-data-stat">
        <span>Reporting Facilities</span>
        <strong>${formatNumber(data.reporting_facilities)}</strong>
      </div>

      <div class="state-data-stat">
        <span>Reporting LGAs</span>
        <strong>${formatNumber(data.reporting_lgas)}</strong>
      </div>

      <div class="state-data-stat">
        <span>Leading Cause</span>
        <strong>${escapeHtml(data.top_cause || "N/A")}</strong>
        <small>
          ${
            data.top_cause
              ? `${Number(data.top_cause_percentage || 0).toFixed(1)}% of observed records`
              : "No cause data available"
          }
        </small>
      </div>

      <div class="state-data-stat">
        <span>Latest Year</span>
        <strong>${data.latest_year || "N/A"}</strong>
      </div>
    </div>

    <div class="state-data-demographics">
      <div class="state-data-section-title">Sex Distribution</div>

      <div class="state-data-sex">
        <span>Male: <strong>${formatNumber(data.male)}</strong></span>
        <span>Female: <strong>${formatNumber(data.female)}</strong></span>
      </div>
    </div>

    ${
      data.estimated_records_status
        ? `
          <div class="state-data-note">
            ${escapeHtml(data.estimated_records_status)}
          </div>
        `
        : ""
    }
  `;
}

function clearSelectedState(container) {
  container
    .querySelectorAll(".geo-state.selected")
    .forEach(state => state.classList.remove("selected"));

  if (container._statePanel) {
    container._statePanel.hidden = true;
  }
}

function createStatePanel() {
  const panel = document.createElement("section");

  panel.className = "state-data-panel";
  panel.hidden = true;
  panel.setAttribute("aria-live", "polite");

  return panel;
}

function createMapTooltip() {
  const tooltip = document.createElement("div");

  tooltip.className = "map-tooltip";
  tooltip.setAttribute("aria-hidden", "true");

  return tooltip;
}

function showMapTooltip(container, stateName, event) {
  const tooltip = container.querySelector(".map-tooltip");

  if (!tooltip) return;

  tooltip.textContent = stateName;
  tooltip.classList.add("visible");

  if (event) {
    moveMapTooltip(container, event);
  }
}

function moveMapTooltip(container, event) {
  const tooltip = container.querySelector(".map-tooltip");

  if (!tooltip) return;

  const rect = container.getBoundingClientRect();

  tooltip.style.left = `${event.clientX - rect.left + 12}px`;
  tooltip.style.top = `${event.clientY - rect.top - 12}px`;
}

function hideMapTooltip(container) {
  const tooltip = container.querySelector(".map-tooltip");

  if (tooltip) {
    tooltip.classList.remove("visible");
  }
}

function showMapError(container, message) {
  container.innerHTML = `
    <div class="map-error">
      <span>MAP UNAVAILABLE</span>
      <small>${escapeHtml(message)}</small>
    </div>
  `;
}

function getStateName(feature) {
  const properties = feature.properties || {};

  const keys = [
    "name",
    "NAME_1",
    "NAME",
    "state",
    "State",
    "STATE",
    "state_name",
    "State_Name",
    "admin1Name"
  ];

  for (const key of keys) {
    if (properties[key]) {
      return normalizeStateName(properties[key]);
    }
  }

  return "";
}

function normalizeStateName(value) {
  return String(value)
    .replace(/\s+State$/i, "")
    .trim();
}

function getGeoBounds(features) {
  const bounds = {
    minLon: Infinity,
    maxLon: -Infinity,
    minLat: Infinity,
    maxLat: -Infinity
  };

  features.forEach(feature => {
    collectCoordinates(feature.geometry, ([lon, lat]) => {
      bounds.minLon = Math.min(bounds.minLon, lon);
      bounds.maxLon = Math.max(bounds.maxLon, lon);
      bounds.minLat = Math.min(bounds.minLat, lat);
      bounds.maxLat = Math.max(bounds.maxLat, lat);
    });
  });

  return bounds;
}

function collectCoordinates(geometry, callback) {
  if (!geometry) return;

  if (geometry.type === "Polygon") {
    geometry.coordinates.forEach(ring => ring.forEach(callback));
  }

  if (geometry.type === "MultiPolygon") {
    geometry.coordinates.forEach(polygon =>
      polygon.forEach(ring => ring.forEach(callback))
    );
  }
}

function createProjection(bounds, width, height) {
  const padding = 25;
  const longitudeRange = bounds.maxLon - bounds.minLon;
  const latitudeRange = bounds.maxLat - bounds.minLat;

  if (!longitudeRange || !latitudeRange) {
    throw new Error("Invalid map boundaries.");
  }

  const scale = Math.min(
    (width - padding * 2) / longitudeRange,
    (height - padding * 2) / latitudeRange
  );

  const mapWidth = longitudeRange * scale;
  const mapHeight = latitudeRange * scale;
  const offsetX = (width - mapWidth) / 2;
  const offsetY = (height - mapHeight) / 2;

  return ([lon, lat]) => [
    offsetX + (lon - bounds.minLon) * scale,
    height - offsetY - (lat - bounds.minLat) * scale
  ];
}

function geometryToPath(geometry, project) {
  if (geometry.type === "Polygon") {
    return polygonToPath(geometry.coordinates, project);
  }

  if (geometry.type === "MultiPolygon") {
    return geometry.coordinates
      .map(polygon => polygonToPath(polygon, project))
      .join(" ");
  }

  return "";
}

function polygonToPath(rings, project) {
  return rings
    .map(ring => {
      if (!ring.length) return "";

      const points = ring.map(project);

      return (
        `M ${points[0][0]} ${points[0][1]} ` +
        points
          .slice(1)
          .map(point => `L ${point[0]} ${point[1]}`)
          .join(" ") +
        " Z"
      );
    })
    .join(" ");
}

function createSvg(tag, attributes) {
  const element = document.createElementNS(
    "http://www.w3.org/2000/svg",
    tag
  );

  Object.entries(attributes).forEach(([key, value]) => {
    element.setAttribute(key, value);
  });

  return element;
}

function formatNumber(value) {
  const number = Number(value);

  return Number.isFinite(number)
    ? number.toLocaleString()
    : "0";
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
```
