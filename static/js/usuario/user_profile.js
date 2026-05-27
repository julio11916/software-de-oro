function toggleUserMenu() {
    const dropdown = document.getElementById("userDropdown");
    if (dropdown) {
        dropdown.classList.toggle("show");
    }
}

function showMessage(message, type) {
    const container = document.getElementById("messageContainer");
    if (!container) return;

    const alertClass = type === "success" ? "alert-success" : "alert-danger";
    const icon = type === "success" ? "fa-check-circle" : "fa-exclamation-circle";

    container.innerHTML = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            <i class="fas ${icon} me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    const closeBtn = container.querySelector(".btn-close");
    if (closeBtn) {
        setTimeout(() => {
            closeBtn.click();
        }, 3000);
    }
}

function showPasswordChangeMessage(message, type) {
    const container = document.getElementById("passwordChangeMessageContainer");
    if (!container) return;

    const alertClass = type === "success" ? "alert-success" : "alert-danger";
    const icon = type === "success" ? "fa-check-circle" : "fa-exclamation-circle";

    container.innerHTML = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            <i class="fas ${icon} me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
}

function setPasswordChangeStep(step) {
    const stepRequest = document.getElementById("passwordStepRequest");
    const stepVerify = document.getElementById("passwordStepVerify");
    const stepForm = document.getElementById("changePasswordForm");

    if (stepRequest) stepRequest.style.display = step === "request" ? "block" : "none";
    if (stepVerify) stepVerify.style.display = step === "verify" ? "block" : "none";
    if (stepForm) stepForm.style.display = step === "form" ? "block" : "none";
}

function enviarCodigoCambioPassword() {
    const btn = document.getElementById("btnEnviarCodigoCambioPassword");
    if (!btn) return;

    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Enviando...';

    fetch("/user/profile/send-password-change-code", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                showPasswordChangeMessage(data.message, "success");
                setPasswordChangeStep("verify");
                const codeInput = document.getElementById("password_change_code_step");
                if (codeInput) codeInput.focus();
            } else {
                showPasswordChangeMessage(data.message || "No fue posible enviar el código.", "error");
            }
        })
        .catch((error) => {
            console.error("Error:", error);
            showPasswordChangeMessage("Error al enviar el código. Intenta nuevamente.", "error");
        })
        .finally(() => {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Solicitar código de seguridad';
        });
}

function verificarCodigoCambioPassword() {
    const codeInput = document.getElementById("password_change_code_step");
    const btn = document.getElementById("btnValidarCodigoCambioPassword");
    const hiddenCode = document.getElementById("password_change_code");
    if (!codeInput || !btn || !hiddenCode) return;

    const codigo = codeInput.value.replace(/\D/g, "").trim();
    if (!/^\d{6}$/.test(codigo)) {
        showPasswordChangeMessage("El código debe tener exactamente 6 dígitos.", "error");
        return;
    }

    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Validando...';

    fetch("/user/profile/verify-password-change-code", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ code: codigo }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                hiddenCode.value = codigo;
                setPasswordChangeStep("form");
                showPasswordChangeMessage(data.message, "success");
                const currentPassword = document.getElementById("current_password");
                if (currentPassword) currentPassword.focus();
                return;
            }

            showPasswordChangeMessage(data.message || "Código inválido.", "error");
        })
        .catch((error) => {
            console.error("Error:", error);
            showPasswordChangeMessage("Error validando el código. Intenta nuevamente.", "error");
        })
        .finally(() => {
            btn.disabled = false;
            btn.innerHTML = "Validar código y continuar";
        });
}

function togglePasswordVisibility(event) {
    const btn = event.currentTarget;
    const targetId = btn.getAttribute("data-target");
    const input = document.getElementById(targetId);
    if (!input) return;

    const icon = btn.querySelector("i");
    if (input.type === "password") {
        input.type = "text";
        if (icon) {
            icon.classList.remove("fa-eye");
            icon.classList.add("fa-eye-slash");
        }
    } else {
        input.type = "password";
        if (icon) {
            icon.classList.remove("fa-eye-slash");
            icon.classList.add("fa-eye");
        }
    }
}

function setupPasswordChangeSection() {
    const btnSendCode = document.getElementById("btnEnviarCodigoCambioPassword");
    if (btnSendCode) {
        btnSendCode.removeEventListener("click", enviarCodigoCambioPassword);
        btnSendCode.addEventListener("click", enviarCodigoCambioPassword);
    }

    const btnVerifyCode = document.getElementById("btnValidarCodigoCambioPassword");
    if (btnVerifyCode) {
        btnVerifyCode.removeEventListener("click", verificarCodigoCambioPassword);
        btnVerifyCode.addEventListener("click", verificarCodigoCambioPassword);
    }

    const btnResendCode = document.getElementById("btnReenviarCodigoCambioPassword");
    if (btnResendCode) {
        btnResendCode.removeEventListener("click", enviarCodigoCambioPassword);
        btnResendCode.addEventListener("click", enviarCodigoCambioPassword);
    }

    const codeInput = document.getElementById("password_change_code_step");
    if (codeInput) {
        codeInput.addEventListener("input", (event) => {
            event.target.value = event.target.value.replace(/\D/g, "").slice(0, 6);
        });
    }

    const form = document.getElementById("changePasswordForm");
    if (form && form.dataset.codeGuardBound !== "1") {
        form.addEventListener("submit", function (event) {
            const hiddenCode = document.getElementById("password_change_code");
            if (!hiddenCode || !/^\d{6}$/.test((hiddenCode.value || "").trim())) {
                event.preventDefault();
                showPasswordChangeMessage(
                    "Primero debes solicitar y validar el código de seguridad para continuar.",
                    "error"
                );
                setPasswordChangeStep("verify");
            }
        });
        form.dataset.codeGuardBound = "1";
    }

    const toggleButtons = document.querySelectorAll("[data-password-toggle]");
    toggleButtons.forEach((btn) => {
        btn.removeEventListener("click", togglePasswordVisibility);
        btn.addEventListener("click", togglePasswordVisibility);
    });
}

function enviarCodigoVerificacion() {
    const btn = document.getElementById("btnEnviarCodigo");
    if (!btn) return;

    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Enviando...';

    fetch("/user/send-verification-code", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                const stepSend = document.getElementById("stepSendCode");
                const stepVerify = document.getElementById("stepVerifyCode");
                if (stepSend) stepSend.style.display = "none";
                if (stepVerify) stepVerify.style.display = "block";
                showMessage(data.message, "success");
                return;
            }

            showMessage(data.message, "error");
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Enviar código';
        })
        .catch((error) => {
            console.error("Error:", error);
            showMessage("Error al enviar el código. Intenta nuevamente.", "error");
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Enviar código';
        });
}

function verificarCodigo(event) {
    event.preventDefault();

    const codigoInput = document.getElementById("codigoVerificacion");
    const btn = document.getElementById("btnVerificar");
    if (!codigoInput || !btn) return;

    const codigo = codigoInput.value.replace(/\s/g, "").trim();
    if (codigo.length !== 6 || !/^\d{6}$/.test(codigo)) {
        showMessage("El código debe tener exactamente 6 dígitos.", "error");
        return;
    }

    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Verificando...';

    fetch("/user/verify-email", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ code: codigo }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                showMessage(data.message, "success");
                setTimeout(() => {
                    location.reload();
                }, 1500);
                return;
            }

            showMessage(data.message, "error");
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-check me-2"></i>Verificar';
            codigoInput.value = "";
        })
        .catch((error) => {
            console.error("Error:", error);
            showMessage("Error al verificar el código. Intenta nuevamente.", "error");
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-check me-2"></i>Verificar';
        });
}

function reenviarCodigo() {
    const codigoInput = document.getElementById("codigoVerificacion");
    const container = document.getElementById("messageContainer");
    if (codigoInput) codigoInput.value = "";
    if (container) container.innerHTML = "";
    enviarCodigoVerificacion();
}

function handleCodigoInput(event) {
    let value = event.target.value.replace(/\D/g, "");
    if (value.length > 6) {
        value = value.substring(0, 6);
    }
    event.target.value = value;
}

function handleCodigoPaste(event) {
    event.preventDefault();
    const pastedText = (event.clipboardData || window.clipboardData).getData("text");
    const cleanedText = pastedText.replace(/\D/g, "").substring(0, 6);
    event.target.value = cleanedText;
}

function handleCodigoKeypress(event) {
    const charCode = event.which ? event.which : event.keyCode;
    if (charCode > 31 && (charCode < 48 || charCode > 57)) {
        event.preventDefault();
        return false;
    }
    return true;
}

function setupCodigoInput() {
    const codigoInput = document.getElementById("codigoVerificacion");
    if (!codigoInput) return;

    codigoInput.removeEventListener("input", handleCodigoInput);
    codigoInput.removeEventListener("paste", handleCodigoPaste);
    codigoInput.removeEventListener("keypress", handleCodigoKeypress);

    codigoInput.addEventListener("input", handleCodigoInput);
    codigoInput.addEventListener("paste", handleCodigoPaste);
    codigoInput.addEventListener("keypress", handleCodigoKeypress);
}

function setupProfileAccountForm() {
    const form = document.querySelector(".profile-account-form");
    if (!form) return;

    const nameInput = form.querySelector("#nombre");
    const phoneInput = form.querySelector("#telefono");
    const addressInput = form.querySelector("#direccion");

    if (phoneInput) {
        phoneInput.addEventListener("input", () => {
            phoneInput.value = phoneInput.value.replace(/\D/g, "").slice(0, 10);
            phoneInput.setCustomValidity("");
        });
    }

    [nameInput, addressInput].forEach((input) => {
        if (!input) return;
        input.addEventListener("input", () => {
            input.setCustomValidity("");
        });
    });

    form.addEventListener("submit", (event) => {
        const nameValue = nameInput ? nameInput.value.trim() : "";
        const phoneValue = phoneInput ? phoneInput.value.replace(/\D/g, "") : "";
        const addressValue = addressInput ? addressInput.value.trim() : "";

        if (nameInput && !nameValue) {
            nameInput.setCustomValidity("El nombre es obligatorio.");
        }
        if (phoneInput && !/^\d{10}$/.test(phoneValue)) {
            phoneInput.setCustomValidity("El celular debe tener exactamente 10 números.");
        }
        if (addressInput && !addressValue) {
            addressInput.setCustomValidity("La dirección es obligatoria.");
        }

        if (!form.checkValidity()) {
            event.preventDefault();
            form.reportValidity();
            return;
        }

        if (nameInput) nameInput.value = nameValue;
        if (phoneInput) phoneInput.value = phoneValue;
        if (addressInput) addressInput.value = addressValue;
    });
}

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".profile-alert .btn-close").forEach((closeBtn) => {
        setTimeout(() => {
            closeBtn.click();
        }, 3000);
    });

    window.addEventListener("click", function (event) {
        if (!event.target.matches(".user-dropdown-btn") && !event.target.closest(".user-dropdown")) {
            const dropdown = document.getElementById("userDropdown");
            if (dropdown && dropdown.classList.contains("show")) {
                dropdown.classList.remove("show");
            }
        }
    });

    const modalVerificacion = document.getElementById("modalVerificacion");
    if (modalVerificacion) {
        modalVerificacion.addEventListener("hidden.bs.modal", function () {
            const stepSend = document.getElementById("stepSendCode");
            const stepVerify = document.getElementById("stepVerifyCode");
            const codigoInput = document.getElementById("codigoVerificacion");
            const container = document.getElementById("messageContainer");
            const btnEnviar = document.getElementById("btnEnviarCodigo");

            if (stepSend) stepSend.style.display = "block";
            if (stepVerify) stepVerify.style.display = "none";
            if (codigoInput) codigoInput.value = "";
            if (container) container.innerHTML = "";
            if (btnEnviar) {
                btnEnviar.disabled = false;
                btnEnviar.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Enviar código';
            }
        });

        modalVerificacion.addEventListener("shown.bs.modal", function () {
            setupCodigoInput();
        });
    }

    const modalSeguridad = document.getElementById("modalSeguridad");
    if (modalSeguridad) {
        modalSeguridad.addEventListener("shown.bs.modal", function () {
            setupPasswordChangeSection();
        });

        modalSeguridad.addEventListener("hidden.bs.modal", function () {
            const container = document.getElementById("passwordChangeMessageContainer");
            if (container) container.innerHTML = "";
            const codeStepInput = document.getElementById("password_change_code_step");
            if (codeStepInput) codeStepInput.value = "";
            const hiddenCode = document.getElementById("password_change_code");
            if (hiddenCode) hiddenCode.value = "";
            const currentPassword = document.getElementById("current_password");
            const newPassword = document.getElementById("new_password");
            if (currentPassword) {
                currentPassword.value = "";
                currentPassword.type = "password";
            }
            if (newPassword) {
                newPassword.value = "";
                newPassword.type = "password";
            }
            document.querySelectorAll("[data-password-toggle] i").forEach((icon) => {
                icon.classList.remove("fa-eye-slash");
                icon.classList.add("fa-eye");
            });
            setPasswordChangeStep("request");
        });
    }

    const focusTarget = new URLSearchParams(window.location.search).get("focus");
    if (focusTarget) {
        const targetInput = focusTarget === "delivery"
            ? document.getElementById("direccion")
            : document.getElementById("telefono");

        if (targetInput) {
            setTimeout(() => {
                targetInput.scrollIntoView({ behavior: "smooth", block: "center" });
                targetInput.focus();
            }, 250);
        }
    }

    setupCodigoInput();
    setupPasswordChangeSection();
    setupProfileAccountForm();
    setPasswordChangeStep("request");
});
