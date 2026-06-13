document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".auth-toast").forEach((toast) => {
        setTimeout(() => {
            toast.classList.add("auth-toast--hide");
            setTimeout(() => toast.remove(), 220);
        }, 3000);
    });

    const form = document.getElementById("registroForm");
    const nombreInput = document.getElementById("nombre");
    const nombreStatus = document.getElementById("nombreStatus");
    const passwordInput = document.getElementById("password");
    const confirmInput = document.getElementById("confirm_password");
    const passwordToggleButtons = document.querySelectorAll("[data-password-toggle]");
    const emailInput = document.getElementById("email");
    const alternateEmailInput = document.getElementById("email_alternativo");
    const alternateEmailStatus = document.getElementById("alternateEmailStatus");
    const cedulaInput = document.getElementById("cedula");
    const telefonoInput = document.getElementById("telefono");
    const emailStatus = document.getElementById("emailStatus");
    const ruleLength = document.getElementById("rule-length");
    const ruleUpper = document.getElementById("rule-uppercase");
    const ruleLower = document.getElementById("rule-lowercase");
    const ruleNumber = document.getElementById("rule-number");
    const ruleSymbol = document.getElementById("rule-symbol");
    const ruleList = document.querySelector(".password-rules");

    if (!form || !nombreInput || !passwordInput || !confirmInput || !emailInput || !emailStatus) {
        return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const nombreRegex = /^[\p{L}\s]+$/u;
    const alternateEmailHelp = alternateEmailStatus?.textContent || "";

    const normalizarNumero = (input, maxLength) => {
        if (!input) {
            return;
        }
        input.value = input.value.replace(/\D/g, "").slice(0, maxLength);
    };

    const validarNombre = () => {
        const nombre = nombreInput.value.trim();
        const valido = Boolean(nombre) && nombreRegex.test(nombre);
        const invalido = Boolean(nombre) && !valido;

        nombreInput.setCustomValidity(
            invalido ? "El nombre completo solo puede contener letras y espacios." : ""
        );
        nombreInput.classList.toggle("is-invalid", invalido);

        if (nombreStatus) {
            nombreStatus.textContent = invalido
                ? "El nombre completo no puede contener números ni símbolos."
                : "Solo se permiten letras y espacios.";
            nombreStatus.classList.toggle("text-danger", invalido);
            nombreStatus.classList.toggle("text-muted", !invalido);
        }
        return valido;
    };

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

    const validarCorreoAlternativo = () => {
        if (!alternateEmailInput) {
            return true;
        }

        const principal = emailInput.value.trim().toLowerCase();
        const alternativo = alternateEmailInput.value.trim().toLowerCase();
        const repetido = Boolean(alternativo && principal && alternativo === principal);
        const mensaje = "El correo alternativo debe ser diferente al correo principal.";

        alternateEmailInput.setCustomValidity(repetido ? mensaje : "");
        alternateEmailInput.classList.toggle("is-invalid", repetido);

        if (alternateEmailStatus) {
            alternateEmailStatus.textContent = repetido ? mensaje : alternateEmailHelp;
            alternateEmailStatus.classList.toggle("text-danger", repetido);
            alternateEmailStatus.classList.toggle("text-muted", !repetido);
        }
        return !repetido;
    };

    const validarConfirmacion = () => {
        if (confirmInput.value && confirmInput.value !== passwordInput.value) {
            confirmInput.setCustomValidity("Las contraseñas no coinciden.");
            return false;
        }
        confirmInput.setCustomValidity("");
        return true;
    };

    const setRuleState = (element, cumple) => {
        if (!element) {
            return;
        }
        element.classList.toggle("password-rule-hidden", cumple);
        element.classList.toggle("text-danger", !cumple);
    };

    const validarPassword = (mostrarErrores = false) => {
        const value = passwordInput.value || "";
        const estados = {
            longitud: value.length >= 8,
            mayuscula: /[A-Z]/.test(value),
            minuscula: /[a-z]/.test(value),
            numero: /\d/.test(value),
            simbolo: /[^A-Za-z0-9]/.test(value)
        };
        const cumpleTodo = Object.values(estados).every(Boolean);

        if (cumpleTodo) {
            ruleList?.classList.add("password-rule-hidden");
            [ruleLength, ruleUpper, ruleLower, ruleNumber, ruleSymbol].forEach((element) => {
                element?.classList.add("password-rule-hidden");
            });
            passwordInput.setCustomValidity("");
            return true;
        }

        if (mostrarErrores || value) {
            ruleList?.classList.remove("password-rule-hidden");
            setRuleState(ruleLength, estados.longitud);
            setRuleState(ruleUpper, estados.mayuscula);
            setRuleState(ruleLower, estados.minuscula);
            setRuleState(ruleNumber, estados.numero);
            setRuleState(ruleSymbol, estados.simbolo);
        } else {
            ruleList?.classList.add("password-rule-hidden");
        }

        const faltantes = [];
        if (!estados.longitud) faltantes.push("mínimo 8 caracteres");
        if (!estados.mayuscula) faltantes.push("una letra mayúscula");
        if (!estados.minuscula) faltantes.push("una letra minúscula");
        if (!estados.numero) faltantes.push("un número");
        if (!estados.simbolo) faltantes.push("un carácter especial");
        passwordInput.setCustomValidity(`A la contraseña le falta: ${faltantes.join(", ")}.`);
        return false;
    };

    const verificarCorreoExistente = async () => {
        const email = emailInput.value.trim().toLowerCase();
        if (!email) {
            setEmailStatus("", "info");
            return false;
        }

        if (!emailRegex.test(email)) {
            setEmailStatus("Debes ingresar un correo electrónico válido.", "error");
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

    nombreInput.addEventListener("input", validarNombre);
    nombreInput.addEventListener("blur", validarNombre);

    passwordInput.addEventListener("input", () => {
        validarPassword(true);
        validarConfirmacion();
    });
    validarPassword(false);
    confirmInput.addEventListener("input", validarConfirmacion);

    passwordToggleButtons.forEach((button) => {
        const target = document.getElementById(button.dataset.target || "");
        if (!target) {
            return;
        }

        button.addEventListener("click", () => {
            const visible = target.type === "text";
            target.type = visible ? "password" : "text";
            button.setAttribute("aria-label", visible ? "Mostrar contraseña" : "Ocultar contraseña");
            button.setAttribute("title", visible ? "Mostrar contraseña" : "Ocultar contraseña");
            const icon = button.querySelector("i");
            if (icon) {
                icon.classList.toggle("fa-eye", visible);
                icon.classList.toggle("fa-eye-slash", !visible);
            }
            target.focus();
        });
    });

    emailInput.addEventListener("input", () => {
        setEmailStatus("", "info");
        validarCorreoAlternativo();
    });

    alternateEmailInput?.addEventListener("input", validarCorreoAlternativo);
    alternateEmailInput?.addEventListener("blur", validarCorreoAlternativo);

    if (cedulaInput) {
        cedulaInput.addEventListener("input", () => normalizarNumero(cedulaInput, 12));
        cedulaInput.addEventListener("blur", () => normalizarNumero(cedulaInput, 12));
    }

    if (telefonoInput) {
        telefonoInput.addEventListener("input", () => normalizarNumero(telefonoInput, 10));
        telefonoInput.addEventListener("blur", () => normalizarNumero(telefonoInput, 10));
    }

    emailInput.addEventListener("blur", async () => {
        await verificarCorreoExistente();
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        validarNombre();
        validarPassword(true);
        validarConfirmacion();
        validarCorreoAlternativo();

        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

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
