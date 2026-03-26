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
            btn.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Enviar Código';
        })
        .catch((error) => {
            console.error("Error:", error);
            showMessage("Error al enviar el código. Intenta nuevamente.", "error");
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Enviar Código';
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

document.addEventListener("DOMContentLoaded", function () {
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
                btnEnviar.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Enviar Código';
            }
        });

        modalVerificacion.addEventListener("shown.bs.modal", function () {
            setupCodigoInput();
        });
    }

    setupCodigoInput();
});
