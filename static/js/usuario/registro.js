document.addEventListener("DOMContentLoaded", () => {
    const passwordInput = document.getElementById("password");
    const confirmInput = document.getElementById("confirm_password");

    if (!passwordInput || !confirmInput) {
        return;
    }

    const validarConfirmacion = () => {
        if (confirmInput.value && confirmInput.value !== passwordInput.value) {
            confirmInput.setCustomValidity("Las contrasenas no coinciden.");
            return;
        }

        confirmInput.setCustomValidity("");
    };

    passwordInput.addEventListener("input", validarConfirmacion);
    confirmInput.addEventListener("input", validarConfirmacion);
});
