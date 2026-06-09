document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("contactForm");
    if (!form) return;

    const phoneInput = document.getElementById("contactTelefono");
    if (phoneInput) {
        phoneInput.addEventListener("input", () => {
            phoneInput.value = phoneInput.value.replace(/\D/g, "").slice(0, 10);
            phoneInput.setCustomValidity("");
        });
    }

    form.addEventListener("submit", (event) => {
        event.preventDefault();

        if (window.CONTACT_CAN_SEND !== true) {
            window.location.href = "/login";
            return;
        }

        const data = new FormData(form);
        const nombre = String(data.get("nombre") || "").trim();
        const email = String(data.get("email") || "").trim();
        const telefono = String(data.get("telefono") || "").replace(/\D/g, "");
        const tipo = String(data.get("tipo") || "").trim();
        const mensaje = String(data.get("mensaje") || "").trim();

        if (phoneInput && !/^\d{10}$/.test(telefono)) {
            phoneInput.setCustomValidity("El celular debe tener exactamente 10 números.");
            phoneInput.reportValidity();
            return;
        }

        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const texto = [
            "Hola, quiero recibir atención de Nachohers.",
            "",
            `Nombre: ${nombre}`,
            `Correo: ${email}`,
            `Celular: ${telefono}`,
            `Tipo de solicitud: ${tipo}`,
            "",
            `Mensaje: ${mensaje}`,
        ].join("\n");

        window.open(`https://wa.me/573229393211?text=${encodeURIComponent(texto)}`, "_blank", "noopener");
    });
});
