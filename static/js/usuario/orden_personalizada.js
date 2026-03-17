(function () {
    const state = {
        genero: "unisex",
        producto: "camiseta",
        tecnica: "impresion",
        color: "blanco",
        estampado: null,
        talla: null,
        pasoActual: 1,
    };

    const priceMap = {
        camiseta: "$ 45.000",
        buso: "$ 78.000",
        gorra: "$ 35.000",
        panoleta: "$ 28.000",
        "buso-manga-larga": "$ 85.000",
    };

    const productLabels = {
        camiseta: "Camiseta",
        buso: "Buso",
        gorra: "Gorra",
        panoleta: "Panuelo",
        "buso-manga-larga": "Buso manga larga",
    };

    const productoInfo = document.getElementById("info-producto");
    const descripcionInfo = document.getElementById("info-informacion");
    const colorInfo = document.getElementById("info-color");
    const estampadoInfo = document.getElementById("info-estampado");
    const tallaInfo = document.getElementById("info-talla");
    const precioInfo = document.getElementById("info-precio");
    const preview = document.getElementById("area-preview");

    function formatLabel(text) {
        if (!text) return "Pendiente";
        return text
            .split("-")
            .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
            .join(" ");
    }

    function setActiveClass(elements, predicate, className) {
        elements.forEach((element) => {
            element.classList.toggle(className, predicate(element));
        });
    }

    function updateSummary() {
        const producto = productLabels[state.producto] || formatLabel(state.producto);
        const tecnica = state.tecnica === "bordado" ? "Bordado" : "Impresion";
        const color = formatLabel(state.color);
        const estampado = state.estampado ? formatLabel(state.estampado) : "Pendiente";
        const talla = state.talla || "Pendiente";

        productoInfo.textContent = producto;
        colorInfo.textContent = color;
        estampadoInfo.textContent = estampado;
        tallaInfo.textContent = talla;
        precioInfo.textContent = priceMap[state.producto] || "$ 45.000";
        descripcionInfo.textContent = `${producto} | ${tecnica} | ${color} | Paso ${state.pasoActual}/4`;

        preview.innerHTML = `
            <div class="orden-preview-canvas__content">
                <i class="fas fa-shirt"></i>
                <p><strong>${producto}</strong></p>
                <p>${tecnica} - ${color} - ${estampado} - ${talla}</p>
            </div>
        `;
    }

    function updateStepIndicators() {
        for (let i = 1; i <= 4; i += 1) {
            const number = document.getElementById(`paso${i}-header`);
            const label = number?.nextElementSibling;
            if (!number || !label) continue;

            number.classList.remove("orden-step__number--active", "orden-step__number--completed");
            label.classList.remove("orden-step__label--active");

            if (i < state.pasoActual) {
                number.classList.add("orden-step__number--completed");
            } else if (i === state.pasoActual) {
                number.classList.add("orden-step__number--active");
                label.classList.add("orden-step__label--active");
            }
        }
    }

    function changeStep(step) {
        document.querySelectorAll(".orden-stage").forEach((section) => {
            section.classList.toggle("orden-stage--hidden", section.id !== `paso${step}`);
        });
        state.pasoActual = step;
        updateStepIndicators();
        updateSummary();
    }

    function updateTabsByProduct() {
        const isSpecial = state.producto === "panoleta" || state.producto === "gorra";
        const tabs = document.querySelectorAll("[data-area]");

        tabs.forEach((tab) => {
            const area = tab.dataset.area;
            const allowed = !isSpecial || area === "impresion-delantera" || area === "impresion-trasera";
            tab.classList.toggle("orden-tab--hidden", !allowed);
            if (!allowed) {
                tab.classList.remove("orden-tab--active");
            }
        });

        if (!document.querySelector(".orden-tab.orden-tab--active:not(.orden-tab--hidden)")) {
            const firstVisible = document.querySelector(".orden-tab:not(.orden-tab--hidden)");
            firstVisible?.classList.add("orden-tab--active");
        }
    }

    function bindSelections() {
        document.querySelectorAll("[data-producto]").forEach((button) => {
            button.addEventListener("click", () => {
                state.producto = button.dataset.producto;
                setActiveClass(
                    document.querySelectorAll("[data-producto]"),
                    (element) => element === button,
                    "orden-product-card--selected"
                );
                updateTabsByProduct();
                updateSummary();
            });
        });

        document.querySelectorAll("[data-tecnica]").forEach((button) => {
            button.addEventListener("click", () => {
                state.tecnica = button.dataset.tecnica;
                setActiveClass(
                    document.querySelectorAll("[data-tecnica]"),
                    (element) => element === button,
                    "orden-option-button--active"
                );
                updateSummary();
            });
        });

        document.querySelectorAll("[data-color]").forEach((button) => {
            button.addEventListener("click", () => {
                state.color = button.dataset.color;
                setActiveClass(
                    document.querySelectorAll("[data-color]"),
                    (element) => element === button,
                    "orden-color-card--selected"
                );
                updateSummary();
            });
        });

        document.querySelectorAll("[data-estampado]").forEach((button) => {
            button.addEventListener("click", () => {
                state.estampado = button.dataset.estampado;
                setActiveClass(
                    document.querySelectorAll("[data-estampado]"),
                    (element) => element === button,
                    "orden-color-card--selected"
                );
                updateSummary();
            });
        });

        document.querySelectorAll("[data-talla]").forEach((button) => {
            button.addEventListener("click", () => {
                state.talla = button.dataset.talla;
                setActiveClass(
                    document.querySelectorAll("[data-talla]"),
                    (element) => element === button,
                    "orden-option-button--active"
                );
                updateSummary();
            });
        });
    }

    function bindNavigation() {
        document.querySelectorAll("[data-siguiente]").forEach((button) => {
            button.addEventListener("click", () => {
                changeStep(Number(button.dataset.siguiente));
            });
        });

        document.querySelectorAll("[data-anterior]").forEach((button) => {
            button.addEventListener("click", () => {
                changeStep(Number(button.dataset.anterior));
            });
        });

        document.getElementById("btn-finalizar")?.addEventListener("click", () => {
            updateSummary();
            alert("La configuracion quedo lista. El siguiente paso sera conectarla al flujo real de carrito.");
        });

        document.getElementById("btn-agregar-carrito")?.addEventListener("click", () => {
            const producto = productLabels[state.producto] || formatLabel(state.producto);
            const tecnica = state.tecnica === "bordado" ? "Bordado" : "Impresion";
            const estampado = state.estampado ? formatLabel(state.estampado) : "Sin estampado";
            const talla = state.talla || "Pendiente";

            alert(
                `Configuracion actual:\nProducto: ${producto}\nTecnica: ${tecnica}\nColor: ${formatLabel(state.color)}\nEstampado: ${estampado}\nTalla: ${talla}`
            );
        });
    }

    function bindTopbar() {
        document.getElementById("btn-salir")?.addEventListener("click", () => {
            window.history.back();
        });

        document.getElementById("btn-menu")?.addEventListener("click", () => {
            alert("Menu en construccion.");
        });

        document.querySelectorAll("[data-area]").forEach((button) => {
            button.addEventListener("click", () => {
                if (button.classList.contains("orden-tab--hidden")) return;
                setActiveClass(
                    document.querySelectorAll("[data-area]"),
                    (element) => element === button,
                    "orden-tab--active"
                );
            });
        });
    }

    bindSelections();
    bindNavigation();
    bindTopbar();
    updateTabsByProduct();
    updateStepIndicators();
    updateSummary();
})();
