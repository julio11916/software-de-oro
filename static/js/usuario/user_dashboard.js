/* JS especifico del dashboard autenticado */

function updatePromotionCountdowns() {
    document.querySelectorAll('.promo-live[data-promo-end]').forEach((element) => {
        const endDateRaw = element.dataset.promoEnd;
        if (!endDateRaw) {
            return;
        }

        const endDate = new Date(`${endDateRaw}T23:59:59`);
        if (Number.isNaN(endDate.getTime())) {
            return;
        }

        const diffMs = endDate.getTime() - Date.now();
        if (diffMs <= 0) {
            element.textContent = 'Promoción vencida.';
            return;
        }

        const totalMinutes = Math.floor(diffMs / 60000);
        const days = Math.floor(totalMinutes / 1440);
        const hours = Math.floor((totalMinutes % 1440) / 60);
        const minutes = totalMinutes % 60;
        const baseText = element.dataset.baseText || element.textContent.trim();
        element.dataset.baseText = baseText;

        let remaining = '';
        if (days > 0) {
            remaining = `${days} día(s), ${hours} hora(s)`;
        } else {
            remaining = `${hours} hora(s), ${minutes} minuto(s)`;
        }

        element.textContent = `${baseText} Quedan ${remaining}.`;
    });
}

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

    updatePromotionCountdowns();
    window.setInterval(updatePromotionCountdowns, 60000);
});
