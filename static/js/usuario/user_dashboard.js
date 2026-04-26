/* JS especifico del dashboard autenticado */

document.addEventListener('DOMContentLoaded', () => {
    const carousel = document.querySelector('#destacadosCarousel');
    if (carousel) {
        const items = carousel.querySelectorAll('.carousel-item');
        if (items.length < 2) {
            carousel.querySelectorAll('.carousel-control-prev, .carousel-control-next')
                .forEach(btn => btn.classList.add('d-none'));
        }
    }
});
