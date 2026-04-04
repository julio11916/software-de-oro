document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("registroForm");
    const passwordInput = document.getElementById("password");
    const confirmInput = document.getElementById("confirm_password");
    const showPasswords = document.getElementById("showPasswords");
    const emailInput = document.getElementById("email");
    const emailStatus = document.getElementById("emailStatus");

    if (!form || !passwordInput || !confirmInput || !showPasswords || !emailInput || !emailStatus) {
        return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    const setEmailStatus = (mensaje, tipo) => {
        emailStatus.textContent = mensaje;
        emailStatus.classList.remove("text-success", "text-danger", "text-muted");
        emailInput.setCustomValidity("");

        if (!mensaje) {
            return;
        }
        if (tipo === "success") {
            emailStatus.classList.add("text-success");
            return;
        }
        if (tipo === "error") {
            emailStatus.classList.add("text-danger");
            emailInput.setCustomValidity(mensaje);
            return;
        }
        emailStatus.classList.add("text-muted");
    };

    const validarConfirmacion = () => {
        if (confirmInput.value && confirmInput.value !== passwordInput.value) {
            confirmInput.setCustomValidity("Las contrasenas no coinciden.");
            return;
        }
        confirmInput.setCustomValidity("");
    };

    const verificarCorreoExistente = async () => {
        const email = emailInput.value.trim().toLowerCase();
        if (!email) {
            setEmailStatus("", "info");
            return false;
        }

        if (!emailRegex.test(email)) {
            setEmailStatus("Debes ingresar un correo electronico valido.", "error");
            return false;
        }

        try {
            const response = await fetch("/registro/check-email", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email })
            });
            const data = await response.json();
            if (!data.success) {
                setEmailStatus(data.message || "No se pudo validar el correo.", "error");
                return false;
            }
            if (data.exists) {
                setEmailStatus(data.message, "error");
                return true;
            }
            setEmailStatus("", "info");
            return false;
        } catch (error) {
            setEmailStatus("No se pudo validar el correo en este momento.", "error");
            return false;
        }
    };

    passwordInput.addEventListener("input", validarConfirmacion);
    confirmInput.addEventListener("input", validarConfirmacion);

    showPasswords.addEventListener("change", () => {
        const tipo = showPasswords.checked ? "text" : "password";
        passwordInput.type = tipo;
        confirmInput.type = tipo;
    });

    emailInput.addEventListener("input", () => {
        setEmailStatus("", "info");
    });

    emailInput.addEventListener("blur", async () => {
        await verificarCorreoExistente();
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        validarConfirmacion();

        const existe = await verificarCorreoExistente();
        if (existe) {
            emailInput.focus();
            emailInput.reportValidity();
            return;
        }

        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        form.submit();
    });
});
