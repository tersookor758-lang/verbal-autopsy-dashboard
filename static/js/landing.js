(function () {

"use strict";

document.addEventListener("DOMContentLoaded", function () {
    initMobileMenu();
    initSmoothScrolling();
    initNigeriaMap();
});

function initMobileMenu() {
    const button = document.getElementById("mobileMenu");
    const navigation = document.querySelector(".main-nav");

    if (!button || !navigation) {
        return;
    }

    button.addEventListener("click", function () {
        const open =
            button.getAttribute("aria-expanded") === "true";

        button.setAttribute(
            "aria-expanded",
            open ? "false" : "true"
        );

        navigation.classList.toggle(
            "mobile-open",
            !open
        );
    });
}

function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(function (link) {
        link.addEventListener("click", function (event) {
            const id = link.getAttribute("href");

            if (!id || id === "#") {
                return;
            }

            const target = document.querySelector(id);

            if (!target) {
                return;
            }

            event.preventDefault();

            target.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });
        });
    });
}

async function initNigeriaMap() {
    const container =
        document.querySelector(".nigeria-map");

    if (!container) {
        return;
    }

    const geojsonUrl =
        container.getAttribute("data-geojson-url");

    if (!geojsonUrl) {
        showMapError(
            container,
            "Map data is unavailable."
        );
        return;
    }

    try {
        const response =
            await fetch(
                geojsonUrl,
                {
                    method: "GET",
                    credentials: "same-origin",
                    cache: "no-store",
                    headers: {
                        Accept: "application/json"
                    }
                }
            );

        if (!response.ok) {
            throw new Error(
                "GeoJSON request failed: HTTP " +
                response.status
            );
        }

        const data =
            await response.json();

        if (
            !data ||
            !Array.isArray(data.features) ||
            data.features.length === 0
        ) {
            throw new Error(
                "GeoJSON contains no features."
            );
        }

        drawNigeriaMap(
            container,
            data
        );
    } catch (error) {
        console.error(
            "Nigeria map error:",
            error
        );

        showMapError(
            container,
            "Unable to load the Nigeria map."
        );
    }
}

function drawNigeriaMap(
    container,
    geojson
) {
    container.innerHTML = "";

    const svgNamespace =
        "http://www.w3.org/2000/svg";

    const svg =
        document.createElementNS(
            svgNamespace,
            "svg"
        );

    svg.classList.add(
        "nigeria-map-svg"
    );

    svg.setAttribute(
        "role",
        "img"
    );

    svg.setAttribute(
        "aria-label",
        "Interactive map of Nigeria"
    );

    svg.setAttribute(
        "preserveAspectRatio",
        "xMidYMid meet"
    );

    const bounds =
        getBounds(
            geojson.features
        );

    if (!bounds) {
        showMapError(
            container,
            "Invalid Nigeria map geometry."
        );
        return;
    }

    const padding = 25;
    const width = 1000;

    const longitudeRange =
        Math.max(
            bounds.maxLongitude -
            bounds.minLongitude,
            0.000001
        );

    const latitudeRange =
        Math.max(
            bounds.maxLatitude -
            bounds.minLatitude,
            0.000001
        );

    const geographicRatio =
        latitudeRange /
        longitudeRange;

    const height =
        Math.max(
            500,
            Math.min(
                1000,
                width *
                geographicRatio
            )
        );

    svg.setAttribute(
        "viewBox",
        "0 0 " +
        width +
        " " +
        height
    );

    const tooltip =
        createTooltip(
            container
        );

    const states = [];

    geojson.features.forEach(
        function (feature) {
            const stateName =
                getStateName(
                    feature
                );

            if (!stateName) {
                return;
            }

            const pathData =
                geometryToPath(
                    feature.geometry,
                    bounds,
                    width,
                    height,
                    padding
                );

            if (!pathData) {
                return;
            }

            const path =
                document.createElementNS(
                    svgNamespace,
                    "path"
                );

            path.setAttribute(
                "d",
                pathData
            );

            path.classList.add(
                "geo-state"
            );

            path.dataset.state =
                stateName;

            path.setAttribute(
                "aria-label",
                stateName
            );

            path.setAttribute(
                "tabindex",
                "0"
            );

            path.style.opacity = "1";
            path.style.visibility = "visible";

            path.addEventListener(
                "mouseenter",
                function (event) {
                    showTooltip(
                        tooltip,
                        stateName,
                        event,
                        container
                    );
                }
            );

            path.addEventListener(
                "mousemove",
                function (event) {
                    moveTooltip(
                        tooltip,
                        event,
                        container
                    );
                }
            );

            path.addEventListener(
                "mouseleave",
                function () {
                    hideTooltip(
                        tooltip
                    );
                }
            );

            path.addEventListener(
                "focus",
                function () {
                    showTooltipFromElement(
                        tooltip,
                        stateName,
                        path,
                        container
                    );
                }
            );

            path.addEventListener(
                "blur",
                function () {
                    hideTooltip(
                        tooltip
                    );
                }
            );

            path.addEventListener(
                "click",
                function () {
                    selectState(
                        stateName,
                        path,
                        states
                    );
                }
            );

            path.addEventListener(
                "keydown",
                function (event) {
                    if (
                        event.key === "Enter" ||
                        event.key === " "
                    ) {
                        event.preventDefault();

                        selectState(
                            stateName,
                            path,
                            states
                        );
                    }
                }
            );

            svg.appendChild(
                path
            );

            states.push(
                path
            );
        }
    );

    if (states.length === 0) {
        showMapError(
            container,
            "No valid Nigerian states were found."
        );
        return;
    }

    container.appendChild(
        svg
    );
}

function getBounds(features) {
    const bounds = {
        minLongitude: Infinity,
        maxLongitude: -Infinity,
        minLatitude: Infinity,
        maxLatitude: -Infinity
    };

    features.forEach(
        function (feature) {
            walkCoordinates(
                feature.geometry,
                function (
                    longitude,
                    latitude
                ) {
                    if (
                        !Number.isFinite(
                            longitude
                        ) ||
                        !Number.isFinite(
                            latitude
                        )
                    ) {
                        return;
                    }

                    bounds.minLongitude =
                        Math.min(
                            bounds.minLongitude,
                            longitude
                        );

                    bounds.maxLongitude =
                        Math.max(
                            bounds.maxLongitude,
                            longitude
                        );

                    bounds.minLatitude =
                        Math.min(
                            bounds.minLatitude,
                            latitude
                        );

                    bounds.maxLatitude =
                        Math.max(
                            bounds.maxLatitude,
                            latitude
                        );
                }
            );
        }
    );

    if (
        !Number.isFinite(
            bounds.minLongitude
        ) ||
        !Number.isFinite(
            bounds.maxLongitude
        ) ||
        !Number.isFinite(
            bounds.minLatitude
        ) ||
        !Number.isFinite(
            bounds.maxLatitude
        )
    ) {
        return null;
    }

    return bounds;
}

function walkCoordinates(
    geometry,
    callback
) {
    if (
        !geometry ||
        !geometry.coordinates
    ) {
        return;
    }

    walkCoordinateArray(
        geometry.coordinates,
        callback
    );
}

function walkCoordinateArray(
    value,
    callback
) {
    if (!Array.isArray(value)) {
        return;
    }

    if (
        value.length >= 2 &&
        typeof value[0] === "number" &&
        typeof value[1] === "number"
    ) {
        callback(
            value[0],
            value[1]
        );
        return;
    }

    value.forEach(
        function (item) {
            walkCoordinateArray(
                item,
                callback
            );
        }
    );
}

function geometryToPath(
    geometry,
    bounds,
    width,
    height,
    padding
) {
    if (!geometry) {
        return "";
    }

    if (
        geometry.type === "Polygon"
    ) {
        return polygonToPath(
            geometry.coordinates,
            bounds,
            width,
            height,
            padding
        );
    }

    if (
        geometry.type === "MultiPolygon"
    ) {
        return geometry.coordinates
            .map(
                function (polygon) {
                    return polygonToPath(
                        polygon,
                        bounds,
                        width,
                        height,
                        padding
                    );
                }
            )
            .join(" ");
    }

    return "";
}

function polygonToPath(
    polygon,
    bounds,
    width,
    height,
    padding
) {
    if (!Array.isArray(polygon)) {
        return "";
    }

    return polygon
        .map(
            function (ring) {
                return ringToPath(
                    ring,
                    bounds,
                    width,
                    height,
                    padding
                );
            }
        )
        .join(" ");
}

function ringToPath(
    ring,
    bounds,
    width,
    height,
    padding
) {
    if (
        !Array.isArray(ring) ||
        ring.length < 2
    ) {
        return "";
    }

    const longitudeRange =
        Math.max(
            bounds.maxLongitude -
            bounds.minLongitude,
            0.000001
        );

    const latitudeRange =
        Math.max(
            bounds.maxLatitude -
            bounds.minLatitude,
            0.000001
        );

    const usableWidth =
        width -
        padding * 2;

    const usableHeight =
        height -
        padding * 2;

    const scale =
        Math.min(
            usableWidth /
            longitudeRange,
            usableHeight /
            latitudeRange
        );

    const actualWidth =
        longitudeRange *
        scale;

    const actualHeight =
        latitudeRange *
        scale;

    const offsetX =
        (
            width -
            actualWidth
        ) / 2;

    const offsetY =
        (
            height -
            actualHeight
        ) / 2;

    let path = "";

    ring.forEach(
        function (
            coordinate,
            index
        ) {
            if (
                !Array.isArray(
                    coordinate
                ) ||
                coordinate.length < 2
            ) {
                return;
            }

            const longitude =
                Number(
                    coordinate[0]
                );

            const latitude =
                Number(
                    coordinate[1]
                );

            if (
                !Number.isFinite(
                    longitude
                ) ||
                !Number.isFinite(
                    latitude
                )
            ) {
                return;
            }

            const x =
                offsetX +
                (
                    longitude -
                    bounds.minLongitude
                ) *
                scale;

            const y =
                offsetY +
                (
                    bounds.maxLatitude -
                    latitude
                ) *
                scale;

            path +=
                (
                    index === 0
                        ? "M "
                        : "L "
                ) +
                x.toFixed(2) +
                " " +
                y.toFixed(2) +
                " ";
        }
    );

    return path + "Z";
}

function getStateName(feature) {
    const properties =
        feature &&
        feature.properties
            ? feature.properties
            : {};

    const names = [
        properties.name,
        properties.NAME,
        properties.NAME_1,
        properties.shapeName,
        properties.shapeName_en,
        properties.admin1Name,
        properties.admin1Name_en,
        properties.st_nm,
        properties.state_name,
        properties.State,
        properties.STATE,
        properties.adm1nm
    ];

    for (
        let i = 0;
        i < names.length;
        i += 1
    ) {
        if (
            typeof names[i] === "string" &&
            names[i].trim()
        ) {
            return names[i].trim();
        }
    }

    return "";
}

function createTooltip(container) {
    const tooltip =
        document.createElement(
            "div"
        );

    tooltip.className =
        "map-tooltip";

    tooltip.setAttribute(
        "aria-hidden",
        "true"
    );

    container.appendChild(
        tooltip
    );

    return tooltip;
}

function showTooltip(
    tooltip,
    stateName,
    event,
    container
) {
    tooltip.textContent =
        stateName;

    tooltip.classList.add(
        "is-visible"
    );

    tooltip.setAttribute(
        "aria-hidden",
        "false"
    );

    moveTooltip(
        tooltip,
        event,
        container
    );
}

function moveTooltip(
    tooltip,
    event,
    container
) {
    if (
        !tooltip.classList.contains(
            "is-visible"
        )
    ) {
        return;
    }

    const rect =
        container.getBoundingClientRect();

    tooltip.style.left =
        (
            event.clientX -
            rect.left +
            12
        ) +
        "px";

    tooltip.style.top =
        Math.max(
            8,
            event.clientY -
            rect.top -
            38
        ) +
        "px";
}

function showTooltipFromElement(
    tooltip,
    stateName,
    element,
    container
) {
    const elementRect =
        element.getBoundingClientRect();

    const containerRect =
        container.getBoundingClientRect();

    tooltip.textContent =
        stateName;

    tooltip.classList.add(
        "is-visible"
    );

    tooltip.setAttribute(
        "aria-hidden",
        "false"
    );

    tooltip.style.left =
        (
            elementRect.left -
            containerRect.left +
            elementRect.width / 2 -
            30
        ) +
        "px";

    tooltip.style.top =
        (
            elementRect.top -
            containerRect.top -
            38
        ) +
        "px";
}

function hideTooltip(tooltip) {
    tooltip.classList.remove(
        "is-visible"
    );

    tooltip.setAttribute(
        "aria-hidden",
        "true"
    );
}

function selectState(
    stateName,
    selectedPath,
    states
) {
    states.forEach(
        function (path) {
            path.classList.remove(
                "is-selected"
            );
        }
    );

    selectedPath.classList.add(
        "is-selected"
    );

    loadStatePercentage(
        stateName
    );
}

async function loadStatePercentage(
    stateName
) {
    const url =
        "/data/state-summary?state=" +
        encodeURIComponent(
            stateName
        );

    try {
        const response =
            await fetch(
                url,
                {
                    method: "GET",
                    credentials: "same-origin",
                    cache: "no-store",
                    headers: {
                        Accept:
                            "application/json"
                    }
                }
            );

        if (!response.ok) {
            throw new Error(
                "State summary failed: HTTP " +
                response.status
            );
        }

        const data =
            await response.json();

        renderStatePercentage(
            data
        );
    } catch (error) {
        console.error(
            "State percentage error:",
            error
        );

        renderStatePercentageError(
            stateName
        );
    }
}

function renderStatePercentage(data) {
    const mapCard =
        document.querySelector(
            ".map-card"
        );

    if (!mapCard) {
        return;
    }

    let message =
        mapCard.querySelector(
            ".state-statistics"
        );

    if (!message) {
        message =
            document.createElement(
                "div"
            );

        message.className =
            "state-statistics";

        mapCard.appendChild(
            message
        );
    }

    const state =
        escapeHtml(
            data.state ||
            "Selected State"
        );

    const value =
        Number(
            data.record_percentage
        );

    const percentage =
        Number.isFinite(value)
            ? value.toFixed(1) + "%"
            : "0.0%";

    message.innerHTML =
        "<strong>" +
        state +
        "</strong>" +
        "<span>" +
        percentage +
        " of recorded deaths" +
        "</span>";

    message.classList.add(
        "is-visible"
    );
}

function renderStatePercentageError(
    stateName
) {
    const mapCard =
        document.querySelector(
            ".map-card"
        );

    if (!mapCard) {
        return;
    }

    let message =
        mapCard.querySelector(
            ".state-statistics"
        );

    if (!message) {
        message =
            document.createElement(
                "div"
            );

        message.className =
            "state-statistics";

        mapCard.appendChild(
            message
        );
    }

    message.innerHTML =
        "<strong>" +
        escapeHtml(
            stateName
        ) +
        "</strong>" +
        "<span>" +
        "Unable to load recorded-death data" +
        "</span>";

    message.classList.add(
        "is-visible"
    );
}

function showMapError(
    container,
    message
) {
    container.innerHTML = "";

    const error =
        document.createElement(
            "div"
        );

    error.className =
        "map-error";

    error.textContent =
        message;

    container.appendChild(
        error
    );
}

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

})();