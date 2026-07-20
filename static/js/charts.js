/*
=========================================================
Verbal Autopsy Outcome Dashboard
File: static/js/charts.js
=========================================================

This file renders all dashboard charts using Chart.js.

Charts:
1. Top States (Bar)
2. Top Causes (Doughnut)
3. Sex Distribution (Pie)
4. Yearly Trend (Line)

Data Source:
window.dashboardStatistics
=========================================================
*/

(function () {
    "use strict";

    /*
    ------------------------------------------------------
    Ensure statistics exist
    ------------------------------------------------------
    */

    const stats = window.dashboardStatistics || {};

    /*
    ------------------------------------------------------
    Store chart instances
    ------------------------------------------------------
    */

    let stateChart = null;
    let causeChart = null;
    let sexChart = null;
    let yearChart = null;

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
        return Array.isArray(value) ? value : [];
    }

    /*
    ------------------------------------------------------
    Chart Colors
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
    STATE BAR CHART
    ------------------------------------------------------
    */

    function renderStateChart() {

        const ctx = getCanvas("stateChart");

        if (!ctx) return;

        destroyChart(stateChart);

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

                        display: false

                    },

                    tooltip: {

                        enabled: true

                    }

                },

                scales: {

                    y: {

                        beginAtZero: true,

                        ticks: {

                            precision: 0

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

                        position: "bottom"

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

                        position: "bottom"

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

                        display: true

                    }

                },

                scales: {

                    y: {

                        beginAtZero: true,

                        ticks: {

                            precision: 0

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
    Initialize
    ------------------------------------------------------
    */

    document.addEventListener("DOMContentLoaded", function () {

        renderAllCharts();

    });

    /*
    ------------------------------------------------------
    Optional Global Access
    ------------------------------------------------------
    */

    window.renderDashboardCharts = renderAllCharts;

})();