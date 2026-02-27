function actualizarFechaHora() {
    const ahora = new Date();

    const opciones = {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    };

    const fecha = ahora.toLocaleDateString('es-ES', opciones);
    const hora = ahora.toLocaleTimeString('es-ES');

    document.getElementById('fechaHora').innerHTML = `
        <div class="text-end">
            <small>${fecha}</small><br>
            <strong>${hora}</strong>
        </div>
    `;
}

setInterval(actualizarFechaHora, 1000);
actualizarFechaHora();
