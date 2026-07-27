/*
=========================================================
Verbal Autopsy Outcome Dashboard
File: static/js/charts.js
=========================================================

Charts:
1. Top States (Bar)
2. Top Causes (Doughnut)
3. Sex Distribution (Pie)
4. Yearly Trend (Line)

Now supports:
✓ Light Mode
✓ Dark Mode
✓ Automatic theme switching
=========================================================
*/

(function () {

    "use strict";

    /*
    ------------------------------------------------------
    Dashboard Statistics
    ------------------------------------------------------
    */

    const stats = window.dashboardStatistics || {};

    /*
    ------------------------------------------------------
    Chart Instances
    ------------------------------------------------------
    */

    let stateChart = null;
    let causeChart = null;
    let sexChart = null;
    let yearChart = null;

    /*
    ------------------------------------------------------
    Color Palette
    ------------------------------------------------------
    */

    const palette = [
        "#0d6efd",
        "#198754",
        "#dc3545",
        "#ffc107",
        "#0dcaf0",
        "#6f42c1",
        "#fd7e14",
        "#20c997",
        "#6610f2",
        "#6c757d"
    ];

    /*
    ------------------------------------------------------
    Theme Detection
    ------------------------------------------------------
    */

    function isDarkMode() {

        return (
            document.documentElement.getAttribute("data-theme") === "dark"
        );

    }

    function getChartTheme() {

        if (isDarkMode()) {

            return {

                text: "#f8f9fa",

                grid: "#444",

                border: "#666"

            };

        }

        return {

            text: "#212529",

            grid: "#dddddd",

            border: "#cccccc"

        };

    }

    /*
    ------------------------------------------------------
    Utility Functions
    ------------------------------------------------------
    */

    function destroyChart(chart) {

        if (chart) {

            chart.destroy();

        }

    }

    function getCanvas(id) {

        const canvas = document.getElementById(id);

        if (!canvas) {

            console.warn(`Canvas '${id}' not found.`);

            return null;

        }

        return canvas.getContext("2d");

    }

    function emptyArray(value) {

        return Array.isArray(value)
            ? value
            : [];

    }
    /*
------------------------------------------------------
STATE BAR CHART
------------------------------------------------------
*/

function renderStateChart() {

    const ctx = getCanvas("stateChart");

    if (!ctx) return;

    destroyChart(stateChart);

    const theme = getChartTheme();

    const topStates = emptyArray(stats.top_states);

    const labels = topStates.map(item => item.state);

    const values = topStates.map(item => item.count);

    stateChart = new Chart(ctx, {

        type: "bar",

        data: {

            labels: labels,

            datasets: [

                {

                    label: "Records",

                    data: values,

                    backgroundColor: palette,

                    borderWidth: 1

                }

            ]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

                legend: {

                    display: false,

                    labels: {

                        color: theme.text

                    }

                },

                tooltip: {

                    enabled: true

                }

            },

            scales: {

                x: {

                    ticks: {

                        color: theme.text

                    },

                    grid: {

                        color: theme.grid

                    }

                },

                y: {

                    beginAtZero: true,

                    ticks: {

                        precision: 0,

                        color: theme.text

                    },

                    grid: {

                        color: theme.grid

                    }

                }

            }

        }

    });

}

/*
------------------------------------------------------
TOP CAUSES DOUGHNUT
------------------------------------------------------
*/

function renderCauseChart() {

    const ctx = getCanvas("causeChart");

    if (!ctx) return;

    destroyChart(causeChart);

    const theme = getChartTheme();

    const causes = emptyArray(stats.top_causes);

    const labels = causes.map(item => item.cause);

    const values = causes.map(item => item.count);

    causeChart = new Chart(ctx, {

        type: "doughnut",

        data: {

            labels: labels,

            datasets: [

                {

                    data: values,

                    backgroundColor: palette,

                    borderWidth: 1

                }

            ]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

                legend: {

                    position: "bottom",

                    labels: {

                        color: theme.text

                    }

                }

            }

        }

    });

}
/*
------------------------------------------------------
SEX PIE CHART
------------------------------------------------------
*/

function renderSexChart() {

    const ctx = getCanvas("sexChart");

    if (!ctx) return;

    destroyChart(sexChart);

    const theme = getChartTheme();

    sexChart = new Chart(ctx, {

        type: "pie",

        data: {

            labels: [

                "Male",

                "Female"

            ],

            datasets: [

                {

                    data: [

                        stats.male_count || 0,

                        stats.female_count || 0

                    ],

                    backgroundColor: [

                        "#0d6efd",

                        "#dc3545"

                    ],

                    borderWidth: 1

                }

            ]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

                legend: {

                    position: "bottom",

                    labels: {

                        color: theme.text

                    }

                }

            }

        }

    });

}

/*
------------------------------------------------------
YEARLY TREND LINE
------------------------------------------------------
*/

function renderYearChart() {

    const ctx = getCanvas("yearChart");

    if (!ctx) return;

    destroyChart(yearChart);

    const theme = getChartTheme();

    const yearly = emptyArray(stats.yearly_trend);

    const labels = yearly.map(item => item.year);

    const values = yearly.map(item => item.count);

    yearChart = new Chart(ctx, {

        type: "line",

        data: {

            labels: labels,

            datasets: [

                {

                    label: "Records",

                    data: values,

                    fill: false,

                    tension: 0.3,

                    borderColor: "#0d6efd",

                    backgroundColor: "#0d6efd",

                    pointRadius: 4,

                    pointHoverRadius: 6

                }

            ]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

                legend: {

                    display: true,

                    labels: {

                        color: theme.text

                    }

                }

            },

            scales: {

                x: {

                    ticks: {

                        color: theme.text

                    },

                    grid: {

                        color: theme.grid

                    }

                },

                y: {

                    beginAtZero: true,

                    ticks: {

                        precision: 0,

                        color: theme.text

                    },

                    grid: {

                        color: theme.grid

                    }

                }

            }

        }

    });

}
/*
------------------------------------------------------
PUBLIC FUNCTION
------------------------------------------------------
*/

function renderAllCharts() {

    renderStateChart();

    renderCauseChart();

    renderSexChart();

    renderYearChart();

}

/*
------------------------------------------------------
Theme Change Listener
------------------------------------------------------
*/

function watchThemeChange() {

    const target = document.documentElement;

    const observer = new MutationObserver(function (mutations) {

        mutations.forEach(function (mutation) {

            if (
                mutation.type === "attributes" &&
                mutation.attributeName === "data-theme"
            ) {

                renderAllCharts();

            }

        });

    });

    observer.observe(target, {

        attributes: true,

        attributeFilter: ["data-theme"]

    });

}

/*
------------------------------------------------------
Initialize
------------------------------------------------------
*/

document.addEventListener("DOMContentLoaded", function () {

    renderAllCharts();

    watchThemeChange();

});

/*
------------------------------------------------------
Optional Global Access
------------------------------------------------------
*/

window.renderDashboardCharts = renderAllCharts;

})();