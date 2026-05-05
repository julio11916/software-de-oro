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

        const updateButtons = () => {
            const maxScrollLeft = Math.max(0, track.scrollWidth - track.clientWidth);
            const hasOverflow = maxScrollLeft > 4;

            prevBtn.disabled = !hasOverflow;
            nextBtn.disabled = !hasOverflow;
        };

        const getScrollStep = () => {
            const firstCard = cards[0];
            const trackStyles = window.getComputedStyle(track);
            const gap = Number.parseFloat(trackStyles.columnGap || trackStyles.gap || '0') || 0;
            const cardWidth = firstCard.getBoundingClientRect().width || 260;

            return Math.max(cardWidth + gap, Math.min(track.clientWidth * 0.85, 340));
        };

        const scrollCards = (direction) => {
            const maxScrollLeft = Math.max(0, track.scrollWidth - track.clientWidth);
            const atStart = track.scrollLeft <= 4;
            const atEnd = track.scrollLeft >= maxScrollLeft - 4;
            let target = track.scrollLeft + (getScrollStep() * direction);

            if (direction > 0 && atEnd) {
                target = 0;
            } else if (direction < 0 && atStart) {
                target = maxScrollLeft;
            } else {
                target = Math.max(0, Math.min(target, maxScrollLeft));
            }

            track.scrollTo({
                left: target,
                behavior: 'smooth'
            });

            window.setTimeout(updateButtons, 280);
        };

        prevBtn.addEventListener('click', () => scrollCards(-1));
        nextBtn.addEventListener('click', () => scrollCards(1));
        track.addEventListener('scroll', updateButtons, { passive: true });
        window.addEventListener('resize', updateButtons);
        window.addEventListener('load', updateButtons);

        updateButtons();
    });
});
