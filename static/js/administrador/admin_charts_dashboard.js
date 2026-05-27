function formatCurrency(value) {
    const number = Number(value || 0);
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        maximumFractionDigits: 0
    }).format(number);
}

function formatCompactCurrency(value) {
    const number = Number(value || 0);
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        notation: 'compact',
        maximumFractionDigits: 1
    }).format(number);
}

function shortenLabel(text, maxLength = 28) {
    const value = String(text || '').trim();
    if (value.length <= maxLength) return value;
    return `${value.slice(0, maxLength - 3).trimEnd()}...`;
}

function buildChartGradient(ctx, colorStart, colorEnd) {
    const gradient = ctx.createLinearGradient(0, 0, 0, 320);
    gradient.addColorStop(0, colorStart);
    gradient.addColorStop(1, colorEnd);
    return gradient;
}

function hasChartLibrary() {
    return typeof window.Chart !== 'undefined';
}

function clearChartBody(canvas) {
    if (!canvas || !canvas.parentElement) return null;
    const body = canvas.parentElement;
    body.querySelectorAll('.chart-fallback, .chart-empty-state').forEach(element => element.remove());
    canvas.hidden = false;
    return body;
}

function showChartEmptyState(canvas, message) {
    const body = clearChartBody(canvas);
    if (!body) return;

    canvas.hidden = true;
    const empty = document.createElement('div');
    empty.className = 'chart-empty-state';
    empty.textContent = message;
    body.appendChild(empty);
}

function renderFallbackBars(canvas, items, options = {}) {
    const body = clearChartBody(canvas);
    if (!body) return;

    canvas.hidden = true;
    const maxValue = Math.max(...items.map(item => Number(item.value || 0)), 1);
    const wrapper = document.createElement('div');
    wrapper.className = 'chart-fallback chart-fallback-bars';

    items.forEach(item => {
        const row = document.createElement('div');
        row.className = 'chart-fallback-row';

        const label = document.createElement('span');
        label.className = 'chart-fallback-label';
        label.textContent = item.label;

        const track = document.createElement('div');
        track.className = 'chart-fallback-track';

        const bar = document.createElement('span');
        bar.className = 'chart-fallback-bar';
        bar.style.width = `${Math.max(4, (Number(item.value || 0) / maxValue) * 100)}%`;

        const value = document.createElement('strong');
        value.className = 'chart-fallback-value';
        value.textContent = options.formatValue ? options.formatValue(item.value) : item.value;

        track.appendChild(bar);
        row.append(label, track, value);
        wrapper.appendChild(row);
    });

    body.appendChild(wrapper);
}

function renderPaymentFallback(canvas, metodosPago) {
    const items = metodosPago.map(item => ({
        label: item.metodo_pago || 'Sin definir',
        value: Number(item.monto || 0)
    }));

    renderFallbackBars(canvas, items, {
        formatValue(value) {
            return formatCurrency(value);
        }
    });
}

function getCommonTooltipStyle() {
    return {
        backgroundColor: 'rgba(10, 22, 43, 0.94)',
        titleColor: '#ffffff',
        bodyColor: '#dce7fb',
        footerColor: '#9cc9ff',
        borderColor: 'rgba(85, 132, 197, 0.25)',
        borderWidth: 1,
        padding: 12,
        cornerRadius: 12
    };
}

function initProductChart(ventasProducto) {
    const canvas = document.getElementById('chartProductos');
    if (!canvas) return;

    const topProducts = [...(ventasProducto || [])]
        .sort((a, b) => Number(b.cantidad || 0) - Number(a.cantidad || 0))
        .slice(0, 10);

    if (!topProducts.length) {
        showChartEmptyState(canvas, 'No hay productos vendidos para graficar en este rango.');
        return;
    }

    if (!hasChartLibrary()) {
        renderFallbackBars(
            canvas,
            topProducts.map(item => ({
                label: item.nombre || 'Producto sin nombre',
                value: Number(item.cantidad || 0)
            }))
        );
        return;
    }

    const ctx = canvas.getContext('2d');
    const labels = topProducts.map(v => v.nombre);
    const data = topProducts.map(v => Number(v.cantidad || 0));
    const chartHeight = Math.max(360, topProducts.length * 42);

    canvas.parentElement.style.height = `${chartHeight}px`;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Cantidad vendida',
                data,
                borderRadius: 10,
                borderSkipped: false,
                backgroundColor: buildChartGradient(ctx, 'rgba(24, 130, 169, 0.92)', 'rgba(10, 41, 98, 0.85)'),
                hoverBackgroundColor: 'rgba(15, 77, 131, 0.94)',
                maxBarThickness: 24
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: { top: 8, right: 14, bottom: 8, left: 8 }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    ...getCommonTooltipStyle(),
                    displayColors: false,
                    callbacks: {
                        title(items) {
                            return items[0]?.label || '';
                        },
                        label(context) {
                            return `Cantidad vendida: ${context.parsed.x}`;
                        },
                        footer(items) {
                            const item = topProducts[items[0]?.dataIndex ?? -1];
                            if (!item) return '';
                            return `Precio ref.: ${formatCurrency(item.precio || 0)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0,
                        color: '#61758a',
                        font: { size: 11, weight: '600' }
                    },
                    grid: {
                        color: 'rgba(15, 64, 122, 0.08)',
                        drawBorder: false
                    },
                    border: { display: false }
                },
                y: {
                    ticks: {
                        color: '#133d76',
                        font: { size: 11, weight: '700' },
                        callback(value, index) {
                            return shortenLabel(labels[index], 30);
                        }
                    },
                    grid: {
                        display: false,
                        drawBorder: false
                    },
                    border: { display: false }
                }
            }
        }
    });
}

function initMonthChart(ventasMes) {
    const canvas = document.getElementById('chartMeses');
    if (!canvas) return;

    if (!ventasMes.length) {
        showChartEmptyState(canvas, 'No hay ventas registradas para graficar en este rango.');
        return;
    }

    if (!hasChartLibrary()) {
        renderFallbackBars(
            canvas,
            ventasMes.map(item => ({
                label: item.mes || 'Sin mes',
                value: Number(item.subtotal || 0)
            })),
            {
                formatValue(value) {
                    return formatCurrency(value);
                }
            }
        );
        return;
    }

    const ctx = canvas.getContext('2d');
    const labels = ventasMes.map(v => v.mes);
    const data = ventasMes.map(v => Number(v.subtotal || 0));

    new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label: 'Total ventas',
                data,
                borderColor: 'rgba(10, 41, 98, 0.92)',
                backgroundColor: buildChartGradient(ctx, 'rgba(24, 130, 169, 0.24)', 'rgba(24, 130, 169, 0.02)'),
                fill: true,
                tension: 0.35,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: '#1882a9',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    ...getCommonTooltipStyle(),
                    callbacks: {
                        label(context) {
                            return `Ventas: ${formatCurrency(context.parsed.y)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: '#61758a',
                        font: { size: 11, weight: '600' }
                    },
                    grid: { display: false },
                    border: { display: false }
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#61758a',
                        font: { size: 11, weight: '600' },
                        callback(value) {
                            return formatCompactCurrency(value);
                        }
                    },
                    grid: {
                        color: 'rgba(15, 64, 122, 0.08)',
                        drawBorder: false
                    },
                    border: { display: false }
                }
            }
        }
    });
}

function initPaymentMethodChart(metodosPago) {
    const canvas = document.getElementById('chartMetodos');
    if (!canvas) return;

    if (!metodosPago.length) {
        showChartEmptyState(canvas, 'No hay métodos de pago para graficar en este rango.');
        return;
    }

    if (!hasChartLibrary()) {
        renderPaymentFallback(canvas, metodosPago);
        return;
    }

    const labels = metodosPago.map(v => v.metodo_pago || 'sin definir');
    const data = metodosPago.map(v => Number(v.monto || 0));

    const ctx = canvas.getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                label: 'Monto por metodo',
                data,
                borderWidth: 0,
                hoverOffset: 10,
                spacing: 3,
                cutout: '62%',
                backgroundColor: [
                    'rgba(10, 41, 98, 0.92)',
                    'rgba(24, 130, 169, 0.88)',
                    'rgba(28, 127, 68, 0.85)',
                    'rgba(208, 135, 32, 0.85)',
                    'rgba(153, 102, 255, 0.82)'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        pointStyle: 'circle',
                        padding: 18,
                        color: '#23415f',
                        font: { size: 11, weight: '600' }
                    }
                },
                tooltip: {
                    ...getCommonTooltipStyle(),
                    callbacks: {
                        label(context) {
                            const total = data.reduce((sum, value) => sum + value, 0);
                            const current = Number(context.parsed || 0);
                            const share = total > 0 ? ((current / total) * 100).toFixed(1) : '0.0';
                            return `${context.label}: ${formatCurrency(current)} (${share}%)`;
                        }
                    }
                }
            }
        }
    });
}

function initCharts(ventasProducto, ventasMes, metodosPago) {
    initProductChart(ventasProducto || []);
    initMonthChart(ventasMes || []);
    initPaymentMethodChart(metodosPago || []);
}

function initRangeFilter() {
    const periodoSelect = document.getElementById('periodoSelect');
    const fechaDesde = document.getElementById('fechaDesde');
    const fechaHasta = document.getElementById('fechaHasta');

    if (!periodoSelect || !fechaDesde || !fechaHasta) return;

    function toggleRango() {
        const habilitar = periodoSelect.value === 'range';
        fechaDesde.disabled = !habilitar;
        fechaHasta.disabled = !habilitar;
    }

    periodoSelect.addEventListener('change', toggleRango);
    toggleRango();
}

function parseChartDataset(chartData, key) {
    try {
        return JSON.parse(chartData.dataset[key] || '[]');
    } catch (error) {
        console.error(`No se pudieron leer los datos de ${key}:`, error);
        return [];
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const chartData = document.getElementById('chartsData');
    if (!chartData) return;

    const ventasProducto = parseChartDataset(chartData, 'productos');
    const ventasMes = parseChartDataset(chartData, 'meses');
    const metodosPago = parseChartDataset(chartData, 'metodos');

    initCharts(ventasProducto, ventasMes, metodosPago);
    initRangeFilter();
});
