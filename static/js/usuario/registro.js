document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("registroForm");
    const passwordInput = document.getElementById("password");
    const confirmInput = document.getElementById("confirm_password");
    const showPasswords = document.getElementById("showPasswords");
    const emailInput = document.getElementById("email");
    const emailStatus = document.getElementById("emailStatus");
    const ruleLength = document.getElementById("rule-length");
    const ruleUpper = document.getElementById("rule-uppercase");
    const ruleLower = document.getElementById("rule-lowercase");
    const ruleNumber = document.getElementById("rule-number");
    const ruleSymbol = document.getElementById("rule-symbol");
    const ruleList = document.querySelector(".password-rules");

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

    const setRuleState = (element, cumple) => {
        if (!element) {
            return;
        }
        if (cumple) {
            element.classList.add("password-rule-hidden");
            element.classList.remove("text-danger", "text-success");
            return;
        }
        element.classList.remove("password-rule-hidden");
        element.classList.remove("text-success");
        element.classList.add("text-danger");
    };

    const validarPassword = () => {
        const value = passwordInput.value || "";
        const tieneLongitud = value.length >= 8;
        const tieneMayus = /[A-Z]/.test(value);
        const tieneMinus = /[a-z]/.test(value);
        const tieneNumero = /\d/.test(value);
        const tieneSimbolo = /[^A-Za-z0-9]/.test(value);

        const cumpleTodo = tieneLongitud && tieneMayus && tieneMinus && tieneNumero && tieneSimbolo;

        if (ruleList) {
            if (cumpleTodo) {
                ruleList.classList.add("password-rule-hidden");
            } else {
                ruleList.classList.remove("password-rule-hidden");
            }
        }

        if (cumpleTodo) {
            [ruleLength, ruleUpper, ruleLower, ruleNumber, ruleSymbol].forEach((el) => {
                if (!el) {
                    return;
                }
                el.classList.add("password-rule-hidden");
                el.classList.remove("text-danger", "text-success");
            });
            passwordInput.setCustomValidity("");
            return;
        }

        setRuleState(ruleLength, tieneLongitud);
        setRuleState(ruleUpper, tieneMayus);
        setRuleState(ruleLower, tieneMinus);
        setRuleState(ruleNumber, tieneNumero);
        setRuleState(ruleSymbol, tieneSimbolo);

        passwordInput.setCustomValidity(
            "La contrasena debe cumplir todas las condiciones."
        );
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

    passwordInput.addEventListener("input", () => {
        validarPassword();
        validarConfirmacion();
    });
    validarPassword();
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
