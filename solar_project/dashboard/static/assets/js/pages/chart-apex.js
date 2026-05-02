'use strict';
setTimeout(function () {
    (function () {
        var sensorSelect = document.querySelector('#sensor-select');
        var currentSensorId = null;
        var sensorByExternalId = {};

        function toSeries(readings, key) {
            return readings
                .filter(function (r) { return r[key] !== null && r[key] !== undefined; })
                .map(function (r) {
                    return { x: r.timestamp, y: Number(r[key]) };
                });
        }

        var voltageChart = null;
        var currentPowerChart = null;

        function sensorLabel() {
            if (!currentSensorId) {
                return '';
            }
            var s = sensorByExternalId[String(currentSensorId)];
            if (!s) {
                return '';
            }
            var parts = [];
            if (s.name) {
                parts.push(s.name);
            }
            if (s.location) {
                parts.push(s.location);
            }
            return parts.join(' — ');
        }

        function updateTitles() {
            var label = sensorLabel();
            var voltageTitle = label ? ('Voltage (Recent) — ' + label) : 'Voltage (Recent)';
            var cpTitle = label ? ('Current + Power (Recent) — ' + label) : 'Current + Power (Recent)';

            if (voltageChart) {
                voltageChart.updateOptions({ title: { text: voltageTitle } }, false, true);
            }
            if (currentPowerChart) {
                currentPowerChart.updateOptions({ title: { text: cpTitle } }, false, true);
            }
        }

        function initCharts() {
            var options = {
                chart: {
                    height: 300,
                    type: 'line',
                    zoom: {
                        enabled: false
                    }
                },
                dataLabels: {
                    enabled: false,
                    width: 2,
                },
                stroke: {
                    curve: 'straight',
                },
                colors: ["#7267EF"],
                series: [{
                    name: "Voltage",
                    data: []
                }],
                title: {
                    text: 'Voltage (Recent)',
                    align: 'left'
                },
                xaxis: {
                    type: 'datetime',
                }
            };

            voltageChart = new ApexCharts(document.querySelector('#line-chart-1'), options);
            voltageChart.render();

            var cpOptions = {
                chart: {
                    height: 350,
                    type: 'area',
                },
                dataLabels: {
                    enabled: false
                },
                stroke: {
                    curve: 'smooth'
                },
                colors: ["#0e9e4a", "#ffa21d"],
                series: [{
                    name: 'Current (A)',
                    data: []
                }, {
                    name: 'Power (W)',
                    data: []
                }],
                title: {
                    text: 'Current + Power (Recent)',
                    align: 'left'
                },
                xaxis: {
                    type: 'datetime',
                }
            };

            currentPowerChart = new ApexCharts(document.querySelector('#area-chart-1'), cpOptions);
            currentPowerChart.render();
        }

        function loadSensors() {
            return fetch('/api/esp/sensors/', { credentials: 'same-origin' })
                .then(function (r) { return r.json(); })
                .then(function (data) {
                    var sensors = (data && data.sensors) ? data.sensors : [];
                    sensorSelect.innerHTML = '';
                    sensorByExternalId = {};
                    sensors.forEach(function (s) {
                        if (s.external_id === null || s.external_id === undefined) {
                            return;
                        }
                        sensorByExternalId[String(s.external_id)] = s;
                        var opt = document.createElement('option');
                        opt.value = String(s.external_id);
                        opt.textContent = s.name + (s.location ? (' — ' + s.location) : '');
                        sensorSelect.appendChild(opt);
                    });
                    var first = sensors.find(function (s) { return s.external_id !== null && s.external_id !== undefined; });
                    if (first) {
                        currentSensorId = String(first.external_id);
                        sensorSelect.value = currentSensorId;
                    }
                    updateTitles();
                });
        }

        function refresh() {
            if (!currentSensorId) {
                return;
            }
            var url = '/api/esp/series/?sensor_id=' + encodeURIComponent(currentSensorId) + '&points=200';
            fetch(url, { credentials: 'same-origin' })
                .then(function (r) { return r.json(); })
                .then(function (data) {
                    var readings = (data && data.readings) ? data.readings : [];
                    if (voltageChart) {
                        var label = sensorLabel();
                        var name = label ? ('Voltage — ' + label) : 'Voltage';
                        voltageChart.updateSeries([{ name: name, data: toSeries(readings, 'voltage') }], true);
                    }
                    if (currentPowerChart) {
                        var label2 = sensorLabel();
                        var cName = label2 ? ('Current (A) — ' + label2) : 'Current (A)';
                        var pName = label2 ? ('Power (W) — ' + label2) : 'Power (W)';
                        currentPowerChart.updateSeries([
                            { name: cName, data: toSeries(readings, 'current') },
                            { name: pName, data: toSeries(readings, 'power') },
                        ], true);
                    }
                })
                .catch(function () { });
        }

        sensorSelect.addEventListener('change', function (e) {
            currentSensorId = e.target.value;
            updateTitles();
            refresh();
        });

        initCharts();
        loadSensors().then(function () {
            refresh();
            setInterval(refresh, 5000);
        });
    })();
    (function () {
        var options = {
            chart: {
                height: 350,
                type: 'bar',
            },
            plotOptions: {
                bar: {
                    horizontal: false,
                    columnWidth: '55%',
                    endingShape: 'rounded'
                },
            },
            dataLabels: {
                enabled: false
            },
            colors: ["#0e9e4a", "#7267EF", "#EA4D4D"],
            stroke: {
                show: true,
                width: 2,
                colors: ['transparent']
            },
            series: [{
                name: 'Net Profit',
                data: [44, 55, 57, 56, 61, 58, 63]
            }, {
                name: 'Revenue',
                data: [76, 85, 101, 98, 87, 105, 91]
            }, {
                name: 'Free Cash Flow',
                data: [35, 41, 36, 26, 45, 48, 52]
            }],
            xaxis: {
                categories: ['Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
            },
            yaxis: {
                title: {
                    text: '$ (thousands)'
                }
            },
            fill: {
                opacity: 1

            },
            tooltip: {
                y: {
                    formatter: function (val) {
                        return "$ " + val + " thousands"
                    }
                }
            }
        }
        var chart = new ApexCharts(
            document.querySelector("#bar-chart-1"),
            options
        );
        chart.render();
    })();
    (function () {
        var options = {
            chart: {
                height: 350,
                type: 'bar',
            },
            plotOptions: {
                bar: {
                    horizontal: true,
                    dataLabels: {
                        position: 'top',
                    },
                }
            },
            colors: ["#7267EF", "#0e9e4a"],
            dataLabels: {
                enabled: true,
                offsetX: -6,
                style: {
                    fontSize: '12px',
                    colors: ['#fff']
                }
            },
            stroke: {
                show: true,
                width: 1,
                colors: ['#fff']
            },
            series: [{
                data: [44, 55, 41, 64, 22, 43, 21]
            }, {
                data: [53, 32, 33, 52, 13, 44, 32]
            }],
            xaxis: {
                categories: [2001, 2002, 2003, 2004, 2005, 2006, 2007],
            },

        }
        var chart = new ApexCharts(
            document.querySelector("#bar-chart-3"),
            options
        );
        chart.render();
    })();
    (function () {
        var options = {
            chart: {
                height: 320,
                type: 'pie',
            },
            labels: ['Team A', 'Team B', 'Team C', 'Team D', 'Team E'],
            series: [44, 55, 13, 43, 22],
            colors: ["#7267EF", "#0e9e4a", "#3ec9d6", "#ffa21d", "#EA4D4D"],
            legend: {
                show: true,
                position: 'bottom',
            },
            dataLabels: {
                enabled: true,
                dropShadow: {
                    enabled: false,
                }
            },
            responsive: [{
                breakpoint: 480,
                options: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }]
        }
        var chart = new ApexCharts(
            document.querySelector("#pie-chart-1"),
            options
        );
        chart.render();
    })();
    (function () {
        var options = {
            chart: {
                height: 320,
                type: 'donut',
            },
            series: [44, 55, 41, 17, 15],
            colors: ["#7267EF", "#0e9e4a", "#3ec9d6", "#ffa21d", "#EA4D4D"],
            legend: {
                show: true,
                position: 'bottom',
            },
            plotOptions: {
                pie: {
                    donut: {
                        labels: {
                            show: true,
                            name: {
                                show: true
                            },
                            value: {
                                show: true
                            }
                        }
                    }
                }
            },
            dataLabels: {
                enabled: true,
                dropShadow: {
                    enabled: false,
                }
            },
            responsive: [{
                breakpoint: 480,
                options: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }]
        }
        var chart = new ApexCharts(
            document.querySelector("#pie-chart-2"),
            options
        );
        chart.render();
    })();
}, 700);
