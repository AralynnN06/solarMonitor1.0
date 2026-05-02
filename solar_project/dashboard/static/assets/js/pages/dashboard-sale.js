'use strict';
document.addEventListener("DOMContentLoaded", function () {
    setTimeout(function () {
        floatchart()
    }, 700);
    // [ campaign-scroll ] start
    var px = new PerfectScrollbar('.feed-scroll', {
        wheelSpeed: .5,
        swipeEasing: 0,
        wheelPropagation: 1,
        minScrollbarLength: 40,
    });
    var px = new PerfectScrollbar('.pro-scroll', {
        wheelSpeed: .5,
        swipeEasing: 0,
        wheelPropagation: 1,
        minScrollbarLength: 40,
    });
    // [ campaign-scroll ] end
});

function floatchart() {
    // [ support-chart ] start
    (function () {
        var options1 = {
            chart: {
                type: 'area',
                height: 85,
                sparkline: {
                    enabled: true
                }
            },
            colors: ["#7267EF"],
            stroke: {
                curve: 'smooth',
                width: 2,
            },
            series: [{
                data: [0, 20, 10, 45, 30, 55, 20, 30, 0]
            }],
            tooltip: {
                fixed: {
                    enabled: false
                },
                x: {
                    show: false
                },
                y: {
                    title: {
                        formatter: function (seriesName) {
                            return 'Energy Usage: '
                        }
                    }
                },
                marker: {
                    show: false
                }
            }
        }
        new ApexCharts(document.querySelector("#support-chart"), options1).render();
        var options2 = {
            chart: {
                type: 'bar',
                height: 85,
                sparkline: {
                    enabled: true
                }
            },
            colors: ["#7267EF"],
            plotOptions: {
                bar: {
                    columnWidth: '70%'
                }
            },
            series: [{
                data: [25, 66, 41, 89, 63, 25, 44, 12, 36, 9, 54, 44, 12, 36, 9, 54, 25, 66, 41, 89, 63, 25, 44, 12, 36, 9, 25, 44, 12, 36, 9, 54]
            }],
            xaxis: {
                crosshairs: {
                    width: 1
                },
            },
            tooltip: {
                fixed: {
                    enabled: false
                },
                x: {
                    show: false
                },
                y: {
                    title: {
                        formatter: function (seriesName) {
                            return ''
                        }
                    }
                },
                marker: {
                    show: false
                }
            }
        }
        new ApexCharts(document.querySelector("#support-chart1"), options2).render();
    })();
    // [ support-chart ] end
    // [ account-chart ] start

    (function () {
        var chartEl = document.querySelector('#account-chart');
        if (!chartEl) {
            return;
        }

        var options = {
            chart: {
                height: 350,
                type: 'bar',
            },
            plotOptions: {
                bar: {
                    columnWidth: '55%',
                    borderRadius: 4,
                }
            },
            colors: ['#7267EF'],
            series: [{
                name: 'Net Energy (kWh)',
                data: []
            }],
            xaxis: {
                categories: []
            },
            tooltip: {
                y: {
                    formatter: function (y) {
                        if (typeof y !== 'undefined') {
                            return y.toFixed(3) + ' kWh';
                        }
                        return y;
                    }
                }
            }
        };

        var chart = new ApexCharts(chartEl, options);
        chart.render();

        var stateSelect = document.getElementById('utility-state');
        var customSelect = document.getElementById('utility-custom');
        var customForm = document.getElementById('utility-custom-form');
        var customName = document.getElementById('utility-custom-name');
        var customRate = document.getElementById('utility-custom-rate');
        var customUrl = document.getElementById('utility-custom-url');
        var customAddBtn = document.getElementById('utility-custom-add');
        var selectedState = null;
        var selectedCustomId = null;

        if (stateSelect) {
            selectedState = localStorage.getItem('utility_state') || 'TX';
            selectedCustomId = localStorage.getItem('utility_custom_id');
        }

        function loadStates() {
            if (!stateSelect) {
                return Promise.resolve();
            }
            return fetch('/api/utility/states/', { credentials: 'same-origin' })
                .then(function (r) { return r.json(); })
                .then(function (data) {
                    var states = (data && data.states) ? data.states : [];
                    stateSelect.innerHTML = '';
                    var customOpt = document.createElement('option');
                    customOpt.value = 'CUSTOM';
                    customOpt.textContent = 'Custom Utility';
                    stateSelect.appendChild(customOpt);
                    states.forEach(function (s) {
                        var opt = document.createElement('option');
                        opt.value = String(s);
                        opt.textContent = String(s);
                        stateSelect.appendChild(opt);
                    });
                    if (states.length > 0) {
                        if (selectedState !== 'CUSTOM' && (!selectedState || states.indexOf(String(selectedState)) === -1)) {
                            selectedState = 'TX';
                        }
                        stateSelect.value = String(selectedState);
                        localStorage.setItem('utility_state', String(selectedState));
                    }
                });
        }

        function loadCustomUtilities() {
            if (!customSelect) {
                return Promise.resolve();
            }
            return fetch('/api/utility/custom/', { credentials: 'same-origin' })
                .then(function (r) { return r.json(); })
                .then(function (data) {
                    var utilities = (data && data.utilities) ? data.utilities : [];
                    customSelect.innerHTML = '';
                    utilities.forEach(function (u) {
                        var opt = document.createElement('option');
                        opt.value = String(u.id);
                        opt.textContent = u.name;
                        customSelect.appendChild(opt);
                    });
                    if (utilities.length > 0) {
                        if (selectedCustomId && utilities.some(function (u) { return String(u.id) === String(selectedCustomId); })) {
                            customSelect.value = String(selectedCustomId);
                        } else {
                            selectedCustomId = String(utilities[0].id);
                            customSelect.value = selectedCustomId;
                            localStorage.setItem('utility_custom_id', selectedCustomId);
                        }
                    }
                });
        }

        function setCustomVisible(visible) {
            if (customSelect) {
                customSelect.style.display = visible ? 'block' : 'none';
            }
            if (customForm) {
                customForm.style.display = visible ? 'block' : 'none';
            }
        }

        if (stateSelect) {
            stateSelect.addEventListener('change', function (e) {
                selectedState = e.target.value;
                localStorage.setItem('utility_state', selectedState);
                setCustomVisible(selectedState === 'CUSTOM');
                refresh();
            });
        }

        if (customSelect) {
            customSelect.addEventListener('change', function (e) {
                selectedCustomId = e.target.value;
                localStorage.setItem('utility_custom_id', selectedCustomId);
                refresh();
            });
        }

        if (customAddBtn) {
            customAddBtn.addEventListener('click', function () {
                var name = customName ? customName.value.trim() : '';
                var rate = customRate ? customRate.value.trim() : '';
                var url = customUrl ? customUrl.value.trim() : '';

                if (!name) {
                    alert('Utility name is required.');
                    return;
                }
                if (!rate) {
                    alert('Rate ($/kWh) is required.');
                    return;
                }
                fetch('/api/utility/custom/', {
                    method: 'POST',
                    credentials: 'same-origin',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: name, rate_usd_per_kwh: rate, rate_source_url: url })
                })
                    .then(function (r) {
                        return r.json().then(function (data) {
                            return { ok: r.ok, data: data };
                        });
                    })
                    .then(function (data) {
                        if (!data.ok) {
                            var msg = (data.data && data.data.error) ? data.data.error : 'Failed to save custom utility.';
                            alert(msg);
                            return;
                        }
                        if (data.data && data.data.utility && data.data.utility.id) {
                            selectedCustomId = String(data.data.utility.id);
                            localStorage.setItem('utility_custom_id', selectedCustomId);
                        }
                        return loadCustomUtilities();
                    })
                    .then(function () {
                        if (customSelect && selectedCustomId) {
                            customSelect.value = selectedCustomId;
                        }
                        refresh();
                    })
                    .catch(function () { });
            });
        }

        function refresh() {
            var rateUrl = '/api/utility/rate/';
            if (selectedState === 'CUSTOM') {
                if (selectedCustomId) {
                    rateUrl += '?utility_id=' + encodeURIComponent(selectedCustomId);
                }
            } else if (selectedState) {
                rateUrl += '?state=' + encodeURIComponent(selectedState);
            }
            Promise.all([
                fetch('/api/esp/net_energy_daily/?days=7', { credentials: 'same-origin' }).then(function (r) { return r.json(); }),
                fetch(rateUrl, { credentials: 'same-origin' }).then(function (r) { return r.json(); }),
            ])
                .then(function (res) {
                    var energy = res[0];
                    var rateData = res[1];

                    var rows = (energy && energy.days) ? energy.days : [];
                    var categories = rows.map(function (x) { return x.day; });
                    var values = rows.map(function (x) {
                        if (x.net_energy_wh === null || x.net_energy_wh === undefined) {
                            return 0;
                        }
                        return Number(x.net_energy_wh) / 1000.0;
                    });

                    var total = values.reduce(function (acc, v) { return acc + v; }, 0);
                    var avg = values.length > 0 ? (total / values.length) : 0;
                    var weeklyEl = document.getElementById('weekly-energy');
                    var avgEl = document.getElementById('avg-daily-energy');
                    if (weeklyEl) {
                        weeklyEl.textContent = total.toFixed(3) + ' kWh';
                    }
                    if (avgEl) {
                        avgEl.textContent = avg.toFixed(3) + ' kWh';
                    }

                    var rate = (rateData && rateData.rate_usd_per_kwh) ? Number(rateData.rate_usd_per_kwh) : 0;
                    var rateEl = document.getElementById('utility-rate');
                    if (rateEl) {
                        rateEl.textContent = '$' + rate.toFixed(3);
                    }

                    var sourceWrap = document.getElementById('utility-source');
                    var sourceLink = document.getElementById('utility-source-link');
                    var url = rateData && rateData.utility ? rateData.utility.rate_source_url : '';
                    if (sourceWrap && sourceLink) {
                        if (url) {
                            sourceWrap.style.display = 'block';
                            sourceLink.href = url;
                        } else {
                            sourceWrap.style.display = 'none';
                            sourceLink.href = '#';
                        }
                    }

                    var savings = total * rate;
                    var savingsEl = document.getElementById('weekly-savings');
                    if (savingsEl) {
                        savingsEl.textContent = '$' + savings.toFixed(2);
                    }

                    chart.updateOptions({ xaxis: { categories: categories } }, false, true);
                    chart.updateSeries([{ name: 'Net Energy (kWh)', data: values }], true);
                })
                .catch(function () { });
        }

        Promise.all([loadStates(), loadCustomUtilities()]).then(function () {
            setCustomVisible(selectedState === 'CUSTOM');
            refresh();
            setInterval(refresh, 10000);
        });
    })();

    // [ account-chart ] end
    // [ satisfaction-chart ] start
    (function () {
        var options = {
            chart: {
                height: 260,
                type: 'pie',
            },
            series: [66, 50, 40, 30],
            labels: ["extremely Satisfied", "Satisfied", "Poor", "Very Poor"],
            legend: {
                show: true,
                offsetY: 50,
            },
            dataLabels: {
                enabled: true,
                dropShadow: {
                    enabled: false,
                }
            },
            theme: {
                monochrome: {
                    enabled: true,
                    color: '#7267EF',
                }
            },
            responsive: [{
                breakpoint: 768,
                options: {
                    chart: {
                        height: 320,

                    },
                    legend: {
                        position: 'bottom',
                        offsetY: 0,
                    }
                }
            }]
        }
        var chart = new ApexCharts(document.querySelector("#satisfaction-chart"), options);
        chart.render();
    })();
    // [ satisfaction-chart ] end
}
