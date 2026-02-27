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

// Función de búsqueda
function buscarProducto() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const productos = document.querySelectorAll('.producto-item');
    let encontrados = 0;

    productos.forEach(producto => {
        const nombre = producto.getAttribute('data-nombre');
        if (nombre.includes(searchTerm)) {
            producto.style.display = 'block';
            encontrados++;
        } else {
            producto.style.display = 'none';
        }
    });

    if (encontrados === 0 && searchTerm !== '') {
        alert('No se encontraron productos con ese nombre.');
    }
}

// Búsqueda en tiempo real
document.getElementById('searchInput').addEventListener('keyup', function (e) {
    if (e.key === 'Enter') {
        buscarProducto();
    }
});

// Actualizar contador del carrito
function actualizarCarrito() {
    // Aquí podrías hacer una petición al servidor para obtener el número real de items
    fetch('/get_cart_count')
        .then(response => response.json())
        .then(data => {
            if (data.count !== undefined) {
                document.getElementById('cartCount').textContent = data.count;
            }
        })
        .catch(() => {
            // Si falla, mostrar 0
            document.getElementById('cartCount').textContent = '0';
        });
}

// Inicializar al cargar la página
document.addEventListener('DOMContentLoaded', function () {
    actualizarCarrito();

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
