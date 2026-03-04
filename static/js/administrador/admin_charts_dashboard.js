function initProductChart(ventasProducto) {
    const canvas = document.getElementById('chartProductos');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const labels = ventasProducto.map(v => v.nombre);
    const data = ventasProducto.map(v => v.cantidad);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Cantidad vendida',
                data,
                backgroundColor: 'rgba(54, 162, 235, 0.6)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

function initMonthChart(ventasMes) {
    const canvas = document.getElementById('chartMeses');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const labels = ventasMes.map(v => v.mes);
    const data = ventasMes.map(v => v.subtotal);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label: 'Total ventas',
                data,
                borderColor: 'rgba(255, 99, 132, 0.8)',
                fill: false,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

function initPaymentMethodChart(metodosPago) {
    const canvas = document.getElementById('chartMetodos');
    if (!canvas) return;

    const labels = metodosPago.map(v => v.metodo_pago || 'sin definir');
    const data = metodosPago.map(v => v.monto || 0);

    const ctx = canvas.getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                label: 'Monto por metodo',
                data,
                backgroundColor: [
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(255, 99, 132, 0.7)',
                    'rgba(255, 205, 86, 0.7)',
                    'rgba(75, 192, 192, 0.7)',
                    'rgba(153, 102, 255, 0.7)'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

function initCharts(ventasProducto, ventasMes, metodosPago) {
    initProductChart(ventasProducto || []);
    initMonthChart(ventasMes || []);
    initPaymentMethodChart(metodosPago || []);
}
