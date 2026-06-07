document.addEventListener("DOMContentLoaded", () => {
    const panels = document.querySelectorAll("[data-recovery-panel]");

    const closePanel = (panel) => {
        const toggle = panel.querySelector("[data-recovery-toggle]");
        const body = panel.querySelector(".recovery-method-panel__body");
        const input = panel.querySelector("input[type='email']");

        if (!toggle || !body || !input) {
            return;
        }

        body.hidden = true;
        toggle.setAttribute("aria-expanded", "false");
        panel.classList.remove("is-open");
        input.removeAttribute("name");
        input.disabled = true;
        input.required = false;
    };

    panels.forEach((panel) => {
        const toggle = panel.querySelector("[data-recovery-toggle]");
        const body = panel.querySelector(".recovery-method-panel__body");
        const input = panel.querySelector("input[type='email']");

        if (!toggle || !body || !input) {
            return;
        }

        toggle.addEventListener("click", () => {
            const wasOpen = !body.hidden;

            panels.forEach(closePanel);

            if (!wasOpen) {
                body.hidden = false;
                toggle.setAttribute("aria-expanded", "true");
                panel.classList.add("is-open");
                input.name = "email";
                input.disabled = false;
                input.required = true;
                input.focus();
            }
        });
    });
});
