document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.js-back-home').forEach((link) => {
        link.addEventListener('click', (event) => {
            if (window.history.length > 1) {
                event.preventDefault();
                window.history.back();
                return;
            }

            const fallbackUrl = link.getAttribute('data-fallback-url');
            if (fallbackUrl) {
                event.preventDefault();
                window.location.href = fallbackUrl;
            }
        });
    });
});
