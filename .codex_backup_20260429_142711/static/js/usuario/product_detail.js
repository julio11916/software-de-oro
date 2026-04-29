// Cambiar slide del carousel
function changeSlide(index) {
    const carousel = document.getElementById('productCarousel');
    const bsCarousel = new bootstrap.Carousel(carousel);
    bsCarousel.to(index);

    // Actualizar thumbnails activos
    document.querySelectorAll('.thumbnail').forEach((thumb, i) => {
        if (i === index) {
            thumb.classList.add('active');
        } else {
            thumb.classList.remove('active');
        }
    });
}

// Actualizar contador del carrito
function actualizarCarrito() {
    fetch('/get_cart_count')
        .then(response => response.json())
        .then(data => {
            if (data.count !== undefined) {
                document.getElementById('cartCount').textContent = data.count;
            }
        })
        .catch(() => {
            document.getElementById('cartCount').textContent = '0';
        });
}

// Actualizar el thumbnail activo cuando cambia el slide
document.getElementById('productCarousel').addEventListener('slid.bs.carousel', function (e) {
    const activeIndex = Array.from(e.target.querySelectorAll('.carousel-item')).indexOf(e.relatedTarget);
    document.querySelectorAll('.thumbnail').forEach((thumb, i) => {
        if (i === activeIndex) {
            thumb.classList.add('active');
        } else {
            thumb.classList.remove('active');
        }
    });
});

// Inicializar al cargar la página
document.addEventListener('DOMContentLoaded', function () {
    actualizarCarrito();
    document.querySelectorAll('.cart-alert .btn-close').forEach((closeBtn) => {
        setTimeout(() => {
            closeBtn.click();
        }, 3000);
    });
    document.querySelectorAll('.thumbnail[data-slide-index]').forEach((thumb) => {
        thumb.addEventListener('click', () => {
            const index = Number(thumb.dataset.slideIndex);
            if (!Number.isNaN(index)) {
                changeSlide(index);
            }
        });
    });
});
