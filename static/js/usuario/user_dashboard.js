/* JS especifico del dashboard autenticado */

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-featured-rail]').forEach((rail) => {
        const track = rail.querySelector('[data-featured-track]');
        const prevBtn = rail.querySelector('[data-featured-prev]');
        const nextBtn = rail.querySelector('[data-featured-next]');
        const cards = Array.from(rail.querySelectorAll('.featured-card'));

        if (!track || !prevBtn || !nextBtn || !cards.length) {
            return;
        }

        const getCardOffsets = () => cards.map((card) => card.offsetLeft);

        const updateButtons = () => {
            const maxScrollLeft = Math.max(0, track.scrollWidth - track.clientWidth);
            const hasOverflow = maxScrollLeft > 8;

            prevBtn.disabled = !hasOverflow || track.scrollLeft <= 8;
            nextBtn.disabled = !hasOverflow || track.scrollLeft >= maxScrollLeft - 8;
        };

        const scrollToCard = (direction) => {
            const current = Math.round(track.scrollLeft);
            const maxScrollLeft = Math.max(0, track.scrollWidth - track.clientWidth);
            const offsets = getCardOffsets();

            let target = current;

            if (direction > 0) {
                target = offsets.find((offset) => offset > current + 16) ?? maxScrollLeft;
            } else {
                const previousOffsets = offsets.filter((offset) => offset < current - 16);
                target = previousOffsets.length ? previousOffsets[previousOffsets.length - 1] : 0;
            }

            track.scrollTo({
                left: Math.max(0, Math.min(target, maxScrollLeft)),
                behavior: 'smooth'
            });
        };

        prevBtn.addEventListener('click', () => scrollToCard(-1));
        nextBtn.addEventListener('click', () => scrollToCard(1));
        track.addEventListener('scroll', updateButtons, { passive: true });
        window.addEventListener('resize', updateButtons);

        updateButtons();
    });
});
