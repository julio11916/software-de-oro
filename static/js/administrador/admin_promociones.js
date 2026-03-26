function updatePromoForceArrows() {
    const controlsByTrack = {};
    document.querySelectorAll('.force-arrow[data-track-id]').forEach((button) => {
        const trackId = button.dataset.trackId;
        if (!trackId) {
            return;
        }
        if (!controlsByTrack[trackId]) {
            controlsByTrack[trackId] = {};
        }
        const direction = button.dataset.direction === 'prev' ? 'prev' : 'next';
        controlsByTrack[trackId][direction] = button;
    });

    Object.entries(controlsByTrack).forEach(([trackId, controls]) => {
        const track = document.getElementById(trackId);
        if (!track) {
            return;
        }

        const maxScrollLeft = Math.max(0, track.scrollWidth - track.clientWidth);
        const hasOverflow = maxScrollLeft > 2;
        const prevButton = controls.prev || null;
        const nextButton = controls.next || null;

        if (prevButton) {
            prevButton.disabled = !hasOverflow;
        }
        if (nextButton) {
            nextButton.disabled = !hasOverflow;
        }
    });
}

let promoForceArrowAnimationFrame = null;
function schedulePromoForceArrowUpdate() {
    if (promoForceArrowAnimationFrame !== null) {
        return;
    }

    promoForceArrowAnimationFrame = window.requestAnimationFrame(() => {
        promoForceArrowAnimationFrame = null;
        updatePromoForceArrows();
    });
}

document.addEventListener('click', (event) => {
    const forceArrow = event.target.closest('.force-arrow');
    if (!forceArrow) {
        return;
    }

    const trackId = forceArrow.dataset.trackId;
    const direction = forceArrow.dataset.direction === 'prev' ? 'prev' : 'next';
    const track = trackId ? document.getElementById(trackId) : null;
    if (!track) {
        return;
    }

    const item = track.querySelector('.force-product-item');
    const styles = window.getComputedStyle(track);
    const gapRaw = styles.gap || styles.columnGap || '0';
    const gap = Number.parseFloat(gapRaw) || 0;
    const step = item ? (item.getBoundingClientRect().width + gap) : track.clientWidth;
    const maxScrollLeft = Math.max(0, track.scrollWidth - track.clientWidth);
    const maxIndex = step > 0 ? Math.round(maxScrollLeft / step) : 0;
    const currentIndex = step > 0 ? Math.round(track.scrollLeft / step) : 0;

    let targetIndex = currentIndex;
    if (direction === 'next') {
        targetIndex = currentIndex >= maxIndex ? 0 : currentIndex + 1;
    } else {
        targetIndex = currentIndex <= 0 ? maxIndex : currentIndex - 1;
    }

    const targetLeft = Math.max(0, Math.min(maxScrollLeft, targetIndex * step));
    track.scrollTo({ left: targetLeft, behavior: 'smooth' });
    schedulePromoForceArrowUpdate();
    setTimeout(schedulePromoForceArrowUpdate, 240);
});

document.addEventListener('DOMContentLoaded', () => {
    const tracks = Array.from(document.querySelectorAll('.force-track'));
    tracks.forEach((track) => {
        track.addEventListener('scroll', schedulePromoForceArrowUpdate, { passive: true });
    });

    window.addEventListener('resize', schedulePromoForceArrowUpdate);
    window.addEventListener('orientationchange', schedulePromoForceArrowUpdate);

    if ('ResizeObserver' in window) {
        const observer = new ResizeObserver(() => {
            schedulePromoForceArrowUpdate();
        });

        tracks.forEach((track) => observer.observe(track));
        document.querySelectorAll('.force-track-wrap, .promo-panel').forEach((block) => {
            observer.observe(block);
        });
    }

    schedulePromoForceArrowUpdate();
});
