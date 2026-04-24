document.addEventListener('DOMContentLoaded', () => {
    const randomChar = (chars) => chars[Math.floor(Math.random() * chars.length)];
    const eyeIcon = `
        <span class="password-icon-eye" aria-hidden="true">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path d="M16 8s-3-5.5-8-5.5S0 8 0 8s3 5.5 8 5.5S16 8 16 8M1.173 8a13 13 0 0 1 1.66-2.043C4.12 4.668 5.88 3.5 8 3.5s3.879 1.168 5.168 2.457A13 13 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755C11.879 11.332 10.12 12.5 8 12.5s-3.879-1.168-5.168-2.457A13 13 0 0 1 1.172 8z"></path>
                <path d="M8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5M4.5 8a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0"></path>
            </svg>
        </span>`;
    const eyeSlashIcon = `
        <span class="password-icon-eye" aria-hidden="true">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path d="M13.359 11.238 15.42 13.3l-.707.707-2.085-2.084A8.7 8.7 0 0 1 8 13.5C3 13.5 0 8 0 8a15.6 15.6 0 0 1 3.231-3.897L1.146 2.018l.708-.707 13.435 13.435-.707.707-2.223-2.223zM11.297 9.176l-1.335-1.335a2 2 0 0 1-2.503-2.503L6.124 4.003A3 3 0 0 0 11.297 9.176"></path>
                <path d="M3.71 5.417A14.6 14.6 0 0 0 1.173 8 13.1 13.1 0 0 0 8 12.5a7.6 7.6 0 0 0 3.879-1.168l-1.442-1.442A3 3 0 0 1 6.11 5.563zM5.35 3.056l1.3 1.3A3 3 0 0 1 9.95 7.657l1.514 1.514A13.1 13.1 0 0 0 14.828 8c-.058-.087-.122-.183-.195-.288-.335-.48-.83-1.12-1.465-1.755C11.879 4.668 10.12 3.5 8 3.5q-.716.002-1.39.128L5.35 3.056z"></path>
            </svg>
        </span>`;

    const generarPasswordSegura = () => {
        const upper = 'ABCDEFGHJKLMNPQRSTUVWXYZ';
        const lower = 'abcdefghijkmnopqrstuvwxyz';
        const nums = '23456789';
        const symbols = '@#$%&*!?';
        const all = upper + lower + nums + symbols;

        const seed = [
            randomChar(upper),
            randomChar(lower),
            randomChar(nums),
            randomChar(symbols)
        ];

        while (seed.length < 12) {
            seed.push(randomChar(all));
        }

        return seed.sort(() => Math.random() - 0.5).join('');
    };

    document.querySelectorAll('.js-toggle-password').forEach((button) => {
        button.addEventListener('click', () => {
            const input = document.querySelector(button.dataset.target || '');
            if (!input) return;
            const nextType = input.type === 'password' ? 'text' : 'password';
            input.type = nextType;
            const visible = nextType === 'text';
            button.innerHTML = visible ? eyeSlashIcon : eyeIcon;
            button.setAttribute('aria-label', visible ? 'Ocultar contraseña' : 'Mostrar contraseña');
            button.setAttribute('title', visible ? 'Ocultar contraseña' : 'Mostrar contraseña');
        });
    });

    document.querySelectorAll('.js-generate-password').forEach((button) => {
        button.addEventListener('click', () => {
            const input = document.querySelector(button.dataset.target || '');
            if (!input) return;
            input.value = generarPasswordSegura();
            input.type = 'text';
            const toggle = document.querySelector(`.js-toggle-password[data-target="${button.dataset.target}"]`);
            if (toggle) {
                toggle.innerHTML = eyeSlashIcon;
                toggle.setAttribute('aria-label', 'Ocultar contraseña');
                toggle.setAttribute('title', 'Ocultar contraseña');
            }
            input.dispatchEvent(new Event('input', { bubbles: true }));
        });
    });

    document.querySelectorAll('.js-copy-password').forEach((button) => {
        button.addEventListener('click', async () => {
            const input = document.querySelector(button.dataset.target || '');
            if (!input || !input.value) return;
            try {
                await navigator.clipboard.writeText(input.value);
                button.textContent = 'Copiado';
                window.setTimeout(() => {
                    button.textContent = 'Copiar';
                }, 1400);
            } catch (error) {
                button.textContent = 'No disponible';
                window.setTimeout(() => {
                    button.textContent = 'Copiar';
                }, 1400);
            }
        });
    });

    document.querySelectorAll('.js-phone-input').forEach((input) => {
        const normalizePhone = () => {
            input.value = input.value.replace(/\D/g, '').slice(0, 10);
            if (input.value.length === 0 || input.value.length === 10) {
                input.setCustomValidity('');
            } else {
                input.setCustomValidity('El teléfono debe tener exactamente 10 números.');
            }
        };

        input.addEventListener('input', normalizePhone);
        input.addEventListener('blur', normalizePhone);
        normalizePhone();
    });
});
