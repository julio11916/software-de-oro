document.addEventListener("DOMContentLoaded", () => {
    const alerts = document.querySelectorAll(".login-alert");
    if (alerts.length) {
        setTimeout(() => {
            alerts.forEach((alertEl) => {
                alertEl.classList.add("auth-toast--hide");
                setTimeout(() => alertEl.remove(), 220);
            });
        }, 3000);
    }

    const loginForm = document.getElementById("loginForm");
    const emailInput = document.getElementById("email");
    const passwordInput = document.getElementById("password");
    const emailAlert = document.getElementById("emailAlert");
    const passwordAlert = document.getElementById("passwordAlert");
    const passwordToggleButtons = document.querySelectorAll("[data-password-toggle]");

    const getToastStack = () => {
        let stack = document.querySelector(".auth-toast-stack");
        if (!stack) {
            stack = document.createElement("div");
            stack.className = "auth-toast-stack";
            stack.setAttribute("role", "status");
            stack.setAttribute("aria-live", "polite");
            document.body.appendChild(stack);
        }
        return stack;
    };

    const showInlineAlert = (el, message) => {
        if (el) {
            el.textContent = "";
            el.classList.add("d-none");
        }
        const toast = document.createElement("div");
        toast.className = "auth-toast auth-toast--danger";
        toast.setAttribute("role", "alert");
        const icon = document.createElement("i");
        icon.className = "fa-solid fa-circle-exclamation";
        const text = document.createElement("span");
        text.textContent = message;
        toast.append(icon, text);
        getToastStack().appendChild(toast);
        setTimeout(() => {
            toast.classList.add("auth-toast--hide");
            setTimeout(() => toast.remove(), 220);
        }, 3000);
    };

    if (loginForm && emailInput && passwordInput) {
        loginForm.addEventListener("submit", (event) => {
            let hasError = false;

            if (!emailInput.value.trim()) {
                showInlineAlert(emailAlert, "Debes ingresar tu correo electrónico.");
                emailInput.classList.add("is-invalid");
                hasError = true;
            } else if (!emailInput.checkValidity()) {
                showInlineAlert(emailAlert, "Ingresa un correo electrónico válido.");
                emailInput.classList.add("is-invalid");
                hasError = true;
            } else {
                emailInput.classList.remove("is-invalid");
            }

            if (!passwordInput.value.trim()) {
                showInlineAlert(passwordAlert, "Debes ingresar tu contraseña.");
                passwordInput.classList.add("is-invalid");
                hasError = true;
            } else {
                passwordInput.classList.remove("is-invalid");
            }

            if (hasError) {
                event.preventDefault();
            }
        });
    }

    passwordToggleButtons.forEach((button) => {
        const target = document.getElementById(button.dataset.target || "");
        if (!target) return;

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
});
