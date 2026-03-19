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
        pañoleta: "$ 28.000",
        "buso-manga-larga": "$ 85.000",
    };

    const productLabels = {
        camiseta: "Camiseta",
        buso: "Buso",
        gorra: "Gorra",
        pañoleta: "Pañoleta",
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

            number.classList.remove("activo", "completado");
            label.classList.remove("activo");

            if (i < state.pasoActual) {
                number.classList.add("completado");
            } else if (i === state.pasoActual) {
                number.classList.add("activo");
                label.classList.add("activo");
            }
        }
    }

    function changeStep(step) {
        document.querySelectorAll(".paso-contenido").forEach((section) => {
            section.classList.toggle("seccion-hidden", section.id !== `paso${step}`);
        });
        state.pasoActual = step;
        updateStepIndicators();
        updateSummary();
    }

    function updateTabsByProduct() {
        const tabs = document.querySelectorAll("[data-area]");
        let allowedAreas = [];
        let defaultActiveArea = null;

        // Definir qué áreas se muestran según el producto
        if (state.producto === "pañoleta") {
            allowedAreas = ["impresion-delantera"];
            defaultActiveArea = "impresion-delantera";
        } else if (state.producto === "gorra") {
            allowedAreas = ["impresion-trasera", "impresion-delantera"];
            defaultActiveArea = "impresion-trasera";
        } else {
            // Para otros productos, mostrar todas
            allowedAreas = [
                "pecho-izquierdo",
                "centro-pecho",
                "centro-ampliado",
                "manga-izquierda",
                "manga-derecha",
                "impresion-trasera",
                "impresion-delantera",
            ];
            defaultActiveArea = "pecho-izquierdo";
        }

        // Remover clase activa de todas y actualizar visibilidad
        tabs.forEach((tab) => {
            const area = tab.dataset.area;
            const isAllowed = allowedAreas.includes(area);
            
            if (!isAllowed) {
                tab.style.display = "none";
                tab.classList.remove("activa");
            } else {
                tab.style.display = "inline-block";
            }
        });

        // Establecer la pestaña activa por defecto según el producto
        tabs.forEach((tab) => {
            tab.classList.remove("activa");
            if (tab.dataset.area === defaultActiveArea && tab.style.display !== "none") {
                tab.classList.add("activa");
            }
        });
    }

    function bindSelections() {
        document.querySelectorAll("[data-producto]").forEach((button) => {
            button.addEventListener("click", () => {
                state.producto = button.dataset.producto;
                setActiveClass(
                    document.querySelectorAll("[data-producto]"),
                    (element) => element === button,
                    "seleccionada"
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
                    "activo"
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
                    "seleccionada"
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
                    "seleccionada"
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
                    "activo"
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

        document.getElementById("btn-agregar-carrito")?.addEventListener("click", async () => {
            // Validar que todos los campos estén completos
            if (!state.talla) {
                alert("Por favor, selecciona una talla antes de agregar al carrito.");
                return;
            }

            const producto = productLabels[state.producto] || formatLabel(state.producto);
            const tecnica = state.tecnica === "bordado" ? "bordado" : "impresion";
            const estampado = state.estampado || "ninguno";
            
            // Mostrar confirmación
            const confirmacion = confirm(
                `¿Agregar al carrito?\n\nProducto: ${producto}\nTécnica: ${tecnica}\nColor: ${formatLabel(state.color)}\nEstampado: ${formatLabel(estampado)}\nTalla: ${state.talla}`
            );
            
            if (!confirmacion) return;

            try {
                const response = await fetch('/add_custom_order', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        producto: state.producto,
                        color: state.color,
                        estampado: estampado,
                        talla: state.talla,
                        tecnica: tecnica
                    })
                });

                const data = await response.json();

                if (data.success) {
                    alert(data.message);
                    // Redirigir al carrito
                    window.location.href = '/cart';
                } else {
                    alert(`Error: ${data.message}`);
                }
            } catch (error) {
                alert(`Error al agregar al carrito: ${error.message}`);
                console.error('Error:', error);
            }
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
                if (button.style.display === "none") return;
                setActiveClass(
                    document.querySelectorAll("[data-area]"),
                    (element) => element === button,
                    "activa"
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
