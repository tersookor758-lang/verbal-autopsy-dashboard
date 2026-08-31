document.addEventListener("DOMContentLoaded", () => {
    const menuButton = document.getElementById("mobileMenu");
    const header = document.querySelector(".site-header");

    if (menuButton && header) {
        const toggleMenu = () => {
            const isOpen = header.classList.toggle("menu-open");

            menuButton.classList.toggle("active", isOpen);

            menuButton.setAttribute(
                "aria-expanded",
                String(isOpen)
            );
        };

        menuButton.setAttribute(
            "aria-expanded",
            "false"
        );

        menuButton.addEventListener(
            "click",
            toggleMenu
        );

        document.querySelectorAll(
            ".nav-links a, .nav-actions a"
        ).forEach(link => {
            link.addEventListener(
                "click",
                () => {
                    header.classList.remove(
                        "menu-open"
                    );

                    menuButton.classList.remove(
                        "active"
                    );

                    menuButton.setAttribute(
                        "aria-expanded",
                        "false"
                    );
                }
            );
        });
    }

    document.querySelectorAll(
        'a[href^="#"]'
    ).forEach(link => {
        link.addEventListener(
            "click",
            event => {
                const targetId =
                    link.getAttribute("href");

                if (
                    !targetId ||
                    targetId === "#"
                ) {
                    return;
                }

                const target =
                    document.querySelector(
                        targetId
                    );

                if (!target) {
                    return;
                }

                event.preventDefault();

                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            }
        );
    });

    initNigeriaMap();
});


async function initNigeriaMap() {
    const mapContainer =
        document.querySelector(".nigeria-map");

    if (!mapContainer) {
        return;
    }

    const geojsonUrl =
        mapContainer.dataset.geojsonUrl;

    if (!geojsonUrl) {
        showMapError(
            mapContainer,
            "MAP CONFIGURATION ERROR",
            "The geographic data endpoint was not configured."
        );

        return;
    }

    try {
        const response = await fetch(
            geojsonUrl,
            {
                method: "GET",
                headers: {
                    Accept:
                        "application/geo+json, application/json"
                },
                credentials: "same-origin"
            }
        );

        if (!response.ok) {
            throw new Error(
                `GeoJSON request failed with status ${response.status}.`
            );
        }

        const geojson =
            await response.json();

        if (
            !geojson ||
            geojson.type !==
                "FeatureCollection" ||
            !Array.isArray(
                geojson.features
            )
        ) {
            throw new Error(
                "The Nigeria GeoJSON is not a valid FeatureCollection."
            );
        }

        if (
            !geojson.features.length
        ) {
            throw new Error(
                "The Nigeria GeoJSON contains no geographic features."
            );
        }

        renderNigeriaMap(
            mapContainer,
            geojson
        );
    } catch (error) {
        console.error(
            "Nigeria map error:",
            error
        );

        showMapError(
            mapContainer,
            "MAP DATA UNAVAILABLE",
            "Unable to load the Nigeria geographic visualization."
        );
    }
}


function renderNigeriaMap(
    container,
    geojson
) {
    const width = 700;
    const height = 700;
    const padding = 65;

    const coordinates = [];

    geojson.features.forEach(
        feature => {
            collectCoordinates(
                feature.geometry,
                coordinates
            );
        }
    );

    if (!coordinates.length) {
        throw new Error(
            "No coordinates found in GeoJSON."
        );
    }

    const bounds =
        getBounds(coordinates);

    const longitudeRange =
        Math.max(
            bounds.maxX - bounds.minX,
            0.001
        );

    const latitudeRange =
        Math.max(
            bounds.maxY - bounds.minY,
            0.001
        );

    const scale = Math.min(
        (width - padding * 2) /
            longitudeRange,
        (height - padding * 2) /
            latitudeRange
    );

    const projectedCoordinates =
        coordinates.map(
            ([longitude, latitude]) => {
                return projectCoordinate(
                    longitude,
                    latitude,
                    bounds,
                    scale,
                    width,
                    height,
                    padding
                );
            }
        );

    const projectedBounds =
        getBounds(
            projectedCoordinates
        );

    const projectedWidth =
        projectedBounds.maxX -
        projectedBounds.minX;

    const projectedHeight =
        projectedBounds.maxY -
        projectedBounds.minY;

    const offsetX =
        (width - projectedWidth) / 2 -
        projectedBounds.minX;

    const offsetY =
        (height - projectedHeight) / 2 -
        projectedBounds.minY;

    const svg =
        createSvgElement(
            "svg",
            {
                viewBox:
                    `0 0 ${width} ${height}`,
                preserveAspectRatio:
                    "xMidYMid meet",
                role: "img",
                "aria-label":
                    "Map of Nigeria showing state boundaries"
            }
        );

    svg.classList.add(
        "nigeria-map-svg"
    );

    const group =
        createSvgElement("g");

    group.setAttribute(
        "transform",
        `translate(${offsetX.toFixed(2)} ${offsetY.toFixed(2)})`
    );

    geojson.features.forEach(
        (feature, index) => {
            const pathData =
                geometryToPath(
                    feature.geometry,
                    coordinate => {
                        return projectCoordinate(
                            coordinate[0],
                            coordinate[1],
                            bounds,
                            scale,
                            width,
                            height,
                            padding
                        );
                    }
                );

            if (!pathData) {
                return;
            }

            const path =
                createSvgElement(
                    "path",
                    {
                        d: pathData
                    }
                );

            const stateName =
                getFeatureName(
                    feature,
                    index
                );

            path.classList.add(
                "geo-state"
            );

            path.dataset.state =
                stateName;

            path.setAttribute(
                "tabindex",
                "0"
            );

            path.setAttribute(
                "role",
                "button"
            );

            path.setAttribute(
                "aria-label",
                stateName
            );

            path.style.setProperty(
                "--map-delay",
                `${Math.min(
                    index * 12,
                    500
                )}ms`
            );

            path.addEventListener(
                "mouseenter",
                event => {
                    showMapTooltip(
                        container,
                        stateName
                    );

                    moveMapTooltip(
                        container,
                        event
                    );
                }
            );

            path.addEventListener(
                "mousemove",
                event => {
                    moveMapTooltip(
                        container,
                        event
                    );
                }
            );

            path.addEventListener(
                "mouseleave",
                () => {
                    hideMapTooltip(
                        container
                    );
                }
            );

            path.addEventListener(
                "focus",
                () => {
                    showMapTooltip(
                        container,
                        stateName
                    );
                }
            );

            path.addEventListener(
                "blur",
                () => {
                    hideMapTooltip(
                        container
                    );
                }
            );

            path.addEventListener(
                "click",
                () => {
                    container.dispatchEvent(
                        new CustomEvent(
                            "state-selected",
                            {
                                detail: {
                                    state:
                                        stateName
                                }
                            }
                        )
                    );
                }
            );

            path.addEventListener(
                "keydown",
                event => {
                    if (
                        event.key ===
                            "Enter" ||
                        event.key === " "
                    ) {
                        event.preventDefault();

                        container.dispatchEvent(
                            new CustomEvent(
                                "state-selected",
                                {
                                    detail: {
                                        state:
                                            stateName
                                    }
                                }
                            )
                        );
                    }
                }
            );

            group.appendChild(
                path
            );
        }
    );

    svg.appendChild(group);

    const tooltip =
        document.createElement("div");

    tooltip.className =
        "map-tooltip";

    tooltip.setAttribute(
        "aria-hidden",
        "true"
    );

    container.replaceChildren(
        svg,
        tooltip
    );
}


function collectCoordinates(
    geometry,
    output
) {
    if (
        !geometry ||
        !geometry.coordinates
    ) {
        return;
    }

    collectNestedCoordinates(
        geometry.coordinates,
        output
    );
}


function collectNestedCoordinates(
    value,
    output
) {
    if (
        Array.isArray(value) &&
        value.length >= 2 &&
        typeof value[0] === "number" &&
        typeof value[1] === "number"
    ) {
        output.push([
            value[0],
            value[1]
        ]);

        return;
    }

    if (!Array.isArray(value)) {
        return;
    }

    value.forEach(item => {
        collectNestedCoordinates(
            item,
            output
        );
    });
}


function getBounds(points) {
    let minX = Infinity;
    let maxX = -Infinity;
    let minY = Infinity;
    let maxY = -Infinity;

    points.forEach(
        ([x, y]) => {
            minX = Math.min(
                minX,
                x
            );

            maxX = Math.max(
                maxX,
                x
            );

            minY = Math.min(
                minY,
                y
            );

            maxY = Math.max(
                maxY,
                y
            );
        }
    );

    return {
        minX,
        maxX,
        minY,
        maxY
    };
}


function projectCoordinate(
    longitude,
    latitude,
    bounds,
    scale,
    width,
    height,
    padding
) {
    const x =
        padding +
        (longitude -
            bounds.minX) *
            scale;

    const y =
        height -
        padding -
        (latitude -
            bounds.minY) *
            scale;

    return [x, y];
}


function geometryToPath(
    geometry,
    projector
) {
    if (!geometry) {
        return "";
    }

    if (
        geometry.type ===
        "Polygon"
    ) {
        return polygonToPath(
            geometry.coordinates,
            projector
        );
    }

    if (
        geometry.type ===
        "MultiPolygon"
    ) {
        return geometry.coordinates
            .map(
                polygon =>
                    polygonToPath(
                        polygon,
                        projector
                    )
            )
            .join(" ");
    }

    return "";
}


function polygonToPath(
    polygons,
    projector
) {
    return polygons
        .map(ring => {
            if (!ring.length) {
                return "";
            }

            return (
                ring
                    .map(
                        (
                            coordinate,
                            index
                        ) => {
                            const [
                                x,
                                y
                            ] =
                                projector(
                                    coordinate
                                );

                            return `${
                                index ===
                                0
                                    ? "M"
                                    : "L"
                            }${x.toFixed(
                                2
                            )},${y.toFixed(
                                2
                            )}`;
                        }
                    )
                    .join(" ") +
                " Z"
            );
        })
        .join(" ");
}


function getFeatureName(
    feature,
    index
) {
    const properties =
        feature &&
        feature.properties
            ? feature.properties
            : {};

    const possibleNames = [
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
        properties.shapeName_1,
        properties.admin1_name
    ];

    const name =
        possibleNames.find(
            value =>
                typeof value ===
                    "string" &&
                value.trim()
        );

    return name
        ? name.trim()
        : `State ${index + 1}`;
}


function createSvgElement(
    tagName,
    attributes = {}
) {
    const element =
        document.createElementNS(
            "http://www.w3.org/2000/svg",
            tagName
        );

    Object.entries(
        attributes
    ).forEach(
        ([name, value]) => {
            element.setAttribute(
                name,
                value
            );
        }
    );

    return element;
}


function showMapTooltip(
    container,
    stateName
) {
    const tooltip =
        container.querySelector(
            ".map-tooltip"
        );

    if (!tooltip) {
        return;
    }

    tooltip.textContent =
        stateName;

    tooltip.setAttribute(
        "aria-hidden",
        "false"
    );

    tooltip.classList.add(
        "visible"
    );
}


function moveMapTooltip(
    container,
    event
) {
    const tooltip =
        container.querySelector(
            ".map-tooltip"
        );

    if (!tooltip) {
        return;
    }

    const bounds =
        container.getBoundingClientRect();

    tooltip.style.left =
        `${
            event.clientX -
            bounds.left +
            14
        }px`;

    tooltip.style.top =
        `${
            event.clientY -
            bounds.top +
            14
        }px`;
}


function hideMapTooltip(
    container
) {
    const tooltip =
        container.querySelector(
            ".map-tooltip"
        );

    if (!tooltip) {
        return;
    }

    tooltip.classList.remove(
        "visible"
    );

    tooltip.setAttribute(
        "aria-hidden",
        "true"
    );
}


function showMapError(
    container,
    title,
    message
) {
    container.replaceChildren();

    const error =
        document.createElement("div");

    error.className =
        "map-error";

    const titleElement =
        document.createElement("span");

    titleElement.textContent =
        title;

    const messageElement =
        document.createElement("small");

    messageElement.textContent =
        message;

    error.append(
        titleElement,
        messageElement
    );

    container.appendChild(error);
}