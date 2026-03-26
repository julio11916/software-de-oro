function updateForceArrows() {
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

let forceArrowAnimationFrame = null;
function scheduleForceArrowUpdate() {
    if (forceArrowAnimationFrame !== null) {
        return;
    }

    forceArrowAnimationFrame = window.requestAnimationFrame(() => {
        forceArrowAnimationFrame = null;
        updateForceArrows();
    });
}

document.addEventListener('click', (event) => {
    const forceArrow = event.target.closest('.force-arrow');
    if (forceArrow) {
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
        scheduleForceArrowUpdate();
        setTimeout(scheduleForceArrowUpdate, 240);
        return;
    }

    const navButton = event.target.closest('.image-nav');
    if (!navButton) {
        return;
    }

    const imageWrap = navButton.closest('.product-image-wrap');
    if (!imageWrap) {
        return;
    }

    const imageElement = imageWrap.querySelector('.js-product-image');
    if (!imageElement) {
        return;
    }

    let images = [];
    try {
        images = JSON.parse(imageElement.dataset.images || '[]');
    } catch (error) {
        images = [];
    }

    if (!Array.isArray(images) || images.length <= 1) {
        return;
    }

    let currentIndex = Number.parseInt(imageElement.dataset.index || '0', 10);
    if (Number.isNaN(currentIndex)) {
        currentIndex = 0;
    }

    const action = navButton.dataset.action === 'prev' ? 'prev' : 'next';
    if (action === 'next') {
        currentIndex = (currentIndex + 1) % images.length;
    } else {
        currentIndex = (currentIndex - 1 + images.length) % images.length;
    }

    const staticPrefix = imageElement.dataset.staticPrefix || '/static/';
    const nextImagePath = String(images[currentIndex] || '').replace(/^\/+/, '');
    imageElement.src = `${staticPrefix}${nextImagePath}`;
    imageElement.dataset.index = String(currentIndex);

    const counter = imageWrap.querySelector('.js-current-index');
    if (counter) {
        counter.textContent = String(currentIndex + 1);
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const tracks = Array.from(document.querySelectorAll('.force-track'));
    tracks.forEach((track) => {
        track.addEventListener('scroll', scheduleForceArrowUpdate, { passive: true });
    });

    window.addEventListener('resize', scheduleForceArrowUpdate);
    window.addEventListener('orientationchange', scheduleForceArrowUpdate);

    if ('ResizeObserver' in window) {
        const observer = new ResizeObserver(() => {
            scheduleForceArrowUpdate();
        });

        tracks.forEach((track) => observer.observe(track));
        document.querySelectorAll('.force-track-wrap, .product-panel').forEach((block) => {
            observer.observe(block);
        });
    }

    scheduleForceArrowUpdate();
});
