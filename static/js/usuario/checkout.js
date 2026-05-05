document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('comprobante_transferencia');
    const form = document.querySelector('.transfer-submit-form');
    const preview = document.querySelector('[data-proof-preview]');
    const previewImage = document.querySelector('[data-proof-preview-image]');
    const clearButton = document.querySelector('[data-proof-clear]');
    const errorMessage = document.querySelector('[data-proof-error]');

    if (!input || !form) {
        return;
    }

    const maxSizeBytes = 3 * 1024 * 1024;
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    let previewUrl = '';

    const showError = (message) => {
        if (!errorMessage) return;
        errorMessage.textContent = message;
        errorMessage.hidden = !message;
    };

    const resetPreview = () => {
        if (previewUrl) {
            URL.revokeObjectURL(previewUrl);
            previewUrl = '';
        }
        if (previewImage) {
            previewImage.removeAttribute('src');
        }
        if (preview) {
            preview.hidden = true;
        }
    };

    const clearFile = () => {
        input.value = '';
        resetPreview();
        showError('');
    };

    const validateFile = () => {
        const file = input.files && input.files[0];
        resetPreview();

        if (!file) {
            showError('Adjunta una captura del comprobante para registrar la transferencia.');
            return false;
        }

        if (!allowedTypes.includes(file.type)) {
            clearFile();
            showError('Formato no permitido. Usa JPG, PNG, GIF o WEBP.');
            return false;
        }

        if (file.size > maxSizeBytes) {
            clearFile();
            showError('La imagen supera el tamano maximo permitido de 3MB.');
            return false;
        }

        previewUrl = URL.createObjectURL(file);
        if (previewImage && preview) {
            previewImage.src = previewUrl;
            preview.hidden = false;
        }
        showError('');
        return true;
    };

    input.addEventListener('change', validateFile);

    if (clearButton) {
        clearButton.addEventListener('click', clearFile);
    }

    form.addEventListener('submit', (event) => {
        if (!validateFile()) {
            event.preventDefault();
            input.focus();
        }
    });
});
