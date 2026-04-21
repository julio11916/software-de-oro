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

    // Carrusel Netflix para Policía
    const netflixCarousel = document.querySelector('#policiaCarousel');
    const prevBtn = document.querySelector('#policiaPrev');
    const nextBtn = document.querySelector('#policiaNext');

    if (netflixCarousel && prevBtn && nextBtn) {
        let currentIndex = 0;
        const itemWidth = 220; // 200px + 20px gap
        const visibleItems = 5;
        const totalItems = netflixCarousel.children.length;
        const maxIndex = Math.max(0, totalItems - visibleItems);

        function updateCarousel() {
            const translateX = -currentIndex * itemWidth;
            netflixCarousel.style.transform = `translateX(${translateX}px)`;
        }

        prevBtn.addEventListener('click', () => {
            if (currentIndex > 0) {
                currentIndex--;
                updateCarousel();
            }
        });

        nextBtn.addEventListener('click', () => {
            if (currentIndex < maxIndex) {
                currentIndex++;
                updateCarousel();
            }
        });

        // Autoplay
        setInterval(() => {
            if (currentIndex < maxIndex) {
                currentIndex++;
            } else {
                currentIndex = 0;
            }
            updateCarousel();
        }, 5000); // 5 segundos
    }
});
