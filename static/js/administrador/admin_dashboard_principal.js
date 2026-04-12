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

function initFeaturedSelectionLimit() {
    const container = document.getElementById('featuredList');
    if (!container) return;

    const max = Number(container.dataset.max || 5);
    const checkboxes = Array.from(container.querySelectorAll('input[type="checkbox"][name="destacados_ids"]'));
    if (!checkboxes.length) return;

    const enforceLimit = (current) => {
        const selected = checkboxes.filter(cb => cb.checked);
        if (selected.length > max && current) {
            current.checked = false;
            alert(`Solo puedes seleccionar hasta ${max} prendas destacadas.`);
            return;
        }
        const limitReached = checkboxes.filter(cb => cb.checked).length >= max;
        checkboxes.forEach(cb => {
            if (!cb.checked) {
                cb.disabled = limitReached;
            }
        });
    };

    checkboxes.forEach(cb => {
        cb.addEventListener('change', () => enforceLimit(cb));
    });
    enforceLimit(null);
}

initFeaturedSelectionLimit();
