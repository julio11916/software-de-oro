document.addEventListener('DOMContentLoaded', () => {
    const phoneInputs = document.querySelectorAll('.js-checkout-phone');
    phoneInputs.forEach((input) => {
        const cleanValue = () => {
            input.value = String(input.value || '').replace(/\D/g, '').slice(0, 10);
        };
        input.addEventListener('input', cleanValue);
        cleanValue();
    });

    const methodCards = document.querySelectorAll('.payment-method-card');
    const submitButton = document.querySelector('.js-cart-submit');
    const submitButtonLabel = document.querySelector('.js-cart-submit-label');
    if (!methodCards.length) {
        return;
    }

    const syncSelected = () => {
        methodCards.forEach((card) => {
            const input = card.querySelector('input[type="radio"]');
            card.classList.toggle('is-selected', Boolean(input && input.checked));
        });

        if (submitButton && submitButtonLabel) {
            const profileIncomplete = submitButton.dataset.profileIncomplete === 'true';
            if (profileIncomplete) {
                submitButtonLabel.textContent = 'Completa tu perfil para continuar';
                return;
            }

            const selectedInput = document.querySelector('.payment-method-card input[type="radio"]:checked');
            const selectedValue = selectedInput ? selectedInput.value : '';
            let label = submitButton.dataset.defaultLabel || 'Continuar segun el metodo elegido';

            if (selectedValue === 'tarjeta') {
                label = submitButton.dataset.tarjetaLabel || label;
            } else if (selectedValue === 'transferencia') {
                label = submitButton.dataset.transferenciaLabel || label;
            }

            submitButtonLabel.textContent = label;
        }
    };

    methodCards.forEach((card) => {
        const input = card.querySelector('input[type="radio"]');
        if (!input) {
            return;
        }

        card.addEventListener('click', () => {
            input.checked = true;
            syncSelected();
        });

        input.addEventListener('change', syncSelected);
    });

    syncSelected();
});
