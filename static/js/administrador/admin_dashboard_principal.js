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

document.addEventListener('click', function (event) {
    const closeButton = event.target.closest('[data-flash-toast-close]');
    if (!closeButton) return;

    const toast = closeButton.closest('.flash-toast');
    if (!toast) return;

    const stack = toast.closest('.flash-toast-stack');
    toast.remove();

    if (stack && !stack.querySelector('.flash-toast')) {
        stack.remove();
    }
});

// Manejo del botón Volver
document.getElementById('backBtn').addEventListener('click', function () {
    if (window.history.length > 1) {
        window.history.back();
    } else {
        window.location.href = '{{ url_for("home") }}';
    }
});

function fadeAndRedirect(event, url) {
    event.preventDefault();
    document.body.classList.add("fade-out");
    setTimeout(() => {
        window.location.href = url;
    }, 300);
}
