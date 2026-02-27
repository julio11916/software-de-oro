// Función para inicializar gráfico de ventas por producto
function initProductChart(ventasProducto) {
    const ctxProd = document.getElementById('chartProductos').getContext('2d');
    new Chart(ctxProd, {
        type: 'bar',
        data: {
            labels: ventasProducto.map(v => v.nombre),
            datasets: [{
                label: 'Cantidad vendida',
                data: ventasProducto.map(v => v.cantidad),
                backgroundColor: 'rgba(54, 162, 235, 0.6)'
            }]
        }
    });
}

// Función para inicializar gráfico de ventas por mes
function initMonthChart(ventasMes) {
    const ctxMes = document.getElementById('chartMeses').getContext('2d');
    new Chart(ctxMes, {
        type: 'line',
        data: {
            labels: ventasMes.map(v => v.mes),
            datasets: [{
                label: 'Total ventas',
                data: ventasMes.map(v => v.subtotal),
                borderColor: 'rgba(255, 99, 132, 0.8)',
                fill: false
            }]
        }
    });
}

// Función principal para inicializar todos los gráficos
function initCharts(ventasProducto, ventasMes) {
    initProductChart(ventasProducto);
    initMonthChart(ventasMes);
}
