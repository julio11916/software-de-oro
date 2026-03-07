const INTENDENCIAS = [
    'Busos',
    'Camibusos',
    'Gorras',
    'Panoletas',
    'Sudaderas',
    'Pantalonetas',
    'Colchas',
    'Tendidos',
    'Chuspas para ropa sucia',
    'Fundas para almohadas',
    'Camuflados'
];

let fuerzaSeleccionada = '';
let intendenciaSeleccionada = '';

// Toggle del menú de usuario (click estático)
function toggleUserMenu() {
    const dropdown = document.getElementById('userDropdown');
    dropdown.classList.toggle('show');
}

function closeUserMenu() {
    const dropdown = document.getElementById('userDropdown');
    dropdown.classList.remove('show');
}

// Cerrar dropdown al hacer click fuera
document.addEventListener('click', function (event) {
    const userDropdown = document.querySelector('.user-dropdown');
    const dropdown = document.getElementById('userDropdown');
    if (dropdown && !userDropdown.contains(event.target)) {
        dropdown.classList.remove('show');
    }
});

// Toggle del submenú en sidebar
function toggleSubmenu(event, element) {
    event.preventDefault();
    const parentLi = element.parentElement;
    const wasActive = parentLi.classList.contains('active');

    // Cerrar todos los submenús
    document.querySelectorAll('.nav-links > li').forEach(li => {
        li.classList.remove('active');
    });

    // Abrir el seleccionado si no estaba activo
    if (!wasActive) {
        parentLi.classList.add('active');
    }
}

// Función para verificar login
function verificarLogin(event) {
    event.preventDefault();
    alert("Debes iniciar sesión o registrarte para comprar.");
    const loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
    loginModal.show();
    return false;
}

// Función de búsqueda
function buscarProducto() {
    const encontrados = aplicarFiltrosCatalogo();
    const searchTerm = document.getElementById('searchInput').value.toLowerCase().trim();
    if (encontrados === 0 && searchTerm !== '') {
        alert('No se encontraron productos con ese nombre.');
    }
}

function seleccionarFuerza(fuerza, button) {
    fuerzaSeleccionada = fuerza.toLowerCase();
    intendenciaSeleccionada = '';

    document.querySelectorAll('.catalog-filter-buttons .catalog-filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    if (button) {
        button.classList.add('active');
    }

    renderizarIntendencias();
    aplicarFiltrosCatalogo();
}

function seleccionarIntendencia(intendencia, button) {
    intendenciaSeleccionada = intendencia.toLowerCase();
    document.querySelectorAll('#intendenciaButtons .catalog-filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    if (button) {
        button.classList.add('active');
    }
    aplicarFiltrosCatalogo();
}

function limpiarFiltroCatalogo() {
    fuerzaSeleccionada = '';
    intendenciaSeleccionada = '';
    document.querySelectorAll('.catalog-filter-btn').forEach(btn => btn.classList.remove('active'));
    renderizarIntendencias();
    aplicarFiltrosCatalogo();
}

function renderizarIntendencias() {
    const container = document.getElementById('intendenciaButtons');
    if (!container) return;

    let html = '<button type="button" class="catalog-filter-btn" onclick="seleccionarIntendencia(\'\', this)">Ver todo</button>';
    INTENDENCIAS.forEach(item => {
        html += `<button type="button" class="catalog-filter-btn" onclick="seleccionarIntendencia('${item}', this)">${item}</button>`;
    });
    container.innerHTML = html;
}

function aplicarFiltrosCatalogo() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase().trim();
    const productos = document.querySelectorAll('.producto-item');
    const summary = document.getElementById('catalogSummary');
    const emptyState = document.getElementById('emptyFilterState');
    let encontrados = 0;

    productos.forEach(producto => {
        const nombre = (producto.getAttribute('data-nombre') || '').toLowerCase();
        const fuerza = (producto.getAttribute('data-fuerza') || '').toLowerCase();
        const intendencia = (producto.getAttribute('data-intendencia') || '').toLowerCase();

        const coincideBusqueda = !searchTerm || nombre.includes(searchTerm);
        const coincideFuerza = !fuerzaSeleccionada || fuerza === fuerzaSeleccionada;
        const coincideIntendencia = !intendenciaSeleccionada || intendencia === intendenciaSeleccionada;
        const visible = coincideBusqueda && coincideFuerza && coincideIntendencia;

        producto.style.display = visible ? 'block' : 'none';
        if (visible) encontrados++;
    });

    if (summary) {
        if (fuerzaSeleccionada && intendenciaSeleccionada) {
            summary.textContent = `Mostrando ${fuerzaSeleccionada} / ${intendenciaSeleccionada}.`;
        } else if (fuerzaSeleccionada) {
            summary.textContent = `Mostrando productos de ${fuerzaSeleccionada}.`;
        } else if (searchTerm) {
            summary.textContent = `Busqueda actual: "${searchTerm}".`;
        } else {
            summary.textContent = 'Explora todos los productos disponibles.';
        }
    }

    if (emptyState) {
        emptyState.style.display = encontrados === 0 ? 'block' : 'none';
    }

    return encontrados;
}

// Búsqueda en tiempo real
document.getElementById('searchInput').addEventListener('keyup', function (e) {
    if (e.key === 'Enter') {
        buscarProducto();
    } else {
        aplicarFiltrosCatalogo();
    }
});

// Actualizar contador del carrito (simulado - deberías conectarlo con tu backend)
function actualizarCarrito() {
    // Aquí deberías obtener el número real de items del carrito
    const cartCount = localStorage.getItem('cartCount') || 0;
    document.getElementById('cartCount').textContent = cartCount;
}

// Función para mostrar carrito
function mostrarCarrito() {
    // Mostrar mensaje y modal de login
    const loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
    loginModal.show();
    // Opcional: mostrar un mensaje dentro del modal
    const modalBody = document.querySelector('#loginModal .modal-body');
    if (modalBody && !document.getElementById('cartLoginMessage')) {
        const mensaje = document.createElement('div');
        mensaje.id = 'cartLoginMessage';
        mensaje.className = 'alert alert-info alert-dismissible fade show mb-3';
        mensaje.innerHTML = '<i class="fas fa-info-circle"></i> Inicia sesión para acceder a tu carrito de compras <button type="button" class="btn-close" data-bs-dismiss="alert"></button>';
        modalBody.insertBefore(mensaje, modalBody.firstChild);
        
        // Eliminar el mensaje después de 5 segundos
        setTimeout(() => {
            if (document.getElementById('cartLoginMessage')) {
                mensaje.remove();
            }
        }, 5000);
    }
}

// Inicializar al cargar la página
document.addEventListener('DOMContentLoaded', function () {
    actualizarCarrito();
    renderizarIntendencias();
    aplicarFiltrosCatalogo();

    // Animación suave al hacer scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Efecto de hover en las tarjetas
    const cards = document.querySelectorAll('.producto-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function () {
            this.style.transition = 'all 0.3s ease';
        });
    });
});

// Filtro por precio (opcional)
function filtrarPorPrecio(min, max) {
    const productos = document.querySelectorAll('.producto-item');
    productos.forEach(producto => {
        const precio = parseFloat(producto.getAttribute('data-precio'));
        if (precio >= min && precio <= max) {
            producto.style.display = 'block';
        } else {
            producto.style.display = 'none';
        }
    });
}
