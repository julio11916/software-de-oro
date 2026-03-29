(function () {
    const state = {
        // Datos personales
        nombre: "",
        direccion: "",
        correo: "",
        telefono: "",
        // Configuración de la prenda
        genero: "unisex",
        identidad: "policia",
        producto: "camiseta",
        tecnica: "impresion",
        color: "blanco",
        estampado: "escudos",
        talla: null,
        pasoActual: 1,
        vistaPrenda: "delantera",
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

    // Elementos del panel derecho (vista previa) - NUEVOS IDs
    const productoInfoPreview = document.getElementById("preview-producto");
    const descripcionInfoPreview = document.getElementById("preview-descripcion");
    const colorInfoPreview = document.getElementById("preview-color");
    const estampadoInfoPreview = document.getElementById("preview-estampado");
    const tallaInfoPreview = document.getElementById("preview-talla");
    const precioInfoPreview = document.getElementById("preview-precio");
    
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

    function getProductIcon() {
        const iconMap = {
            camiseta: "👕",
            buso: "👔",
            gorra: "🧢",
            pañoleta: "🧣",
            "buso-manga-larga": "👚",
        };
        
        return iconMap[state.producto] || "👕";
    }

    function getProductImage() {
        // PAÑOLETA: Mostrar colores en paso 3, sino mostrar frente/espalda
        if (state.producto.toLowerCase() === "pañoleta") {
            const panoletaBase = "/static/img/prendas/panoletas";
            
            // En paso 3 (Color), mostrar la pañoleta con el color seleccionado
            if (state.pasoActual === 3) {
                const colorMap = {
                    blanco: "panoleta_blanco.png",
                    negro: "panoleta_negro.png",
                    "verde-claro": "panoleta_verde.png",
                    beiches: "panoleta_beiches.png",
                };
                
                const colorFile = colorMap[state.color];
                if (colorFile) {
                    return `${panoletaBase}/${colorFile}`;
                }
            }

            // En pasos 1-2, mostrar frente/espalda según vistaPrenda
            return state.vistaPrenda === "trasera"
                ? `${panoletaBase}/panoleta_espalda.png`
                : `${panoletaBase}/panoleta_frente.png`;
        }

        // BUSO: Mostrar colores en paso 3, sino mostrar frente/espalda
        if (state.producto.toLowerCase() === "buso") {
            const busoBase = "/static/img/prendas/busos";
            
            // En paso 3 (Color), mostrar el buso con el color seleccionado
            if (state.pasoActual === 3) {
                const colorMap = {
                    blanco: "buso_blanco.png",
                    negro: "buso_negro.png",
                    "verde-claro": "buso_verde.png",
                    beiches: "buso_beiches.png",
                };
                
                const colorFile = colorMap[state.color];
                if (colorFile) {
                    return `${busoBase}/${colorFile}`;
                }
            }

            // En pasos 1-2, mostrar frente/espalda según vistaPrenda
            return state.vistaPrenda === "trasera"
                ? `${busoBase}/Buso_de_espalda_-removebg-preview.png`
                : `${busoBase}/Buso_de_frente-removebg-preview.png`;
        }

        // BUSO MANGA LARGA: Mostrar colores en paso 3, sino mostrar frente/espalda
        if (state.producto.toLowerCase() === "buso-manga-larga") {
            const busoMangoBase = "/static/img/prendas/busos-manga-larga";
            
            // En paso 3 (Color), mostrar el buso manga larga con el color seleccionado
            if (state.pasoActual === 3) {
                const colorMap = {
                    blanco: "buso_manga_larga_blanco.png",
                    negro: "buso_manga_larga_negro.png",
                    "verde-claro": "buso_manga_larga_verde.png",
                    beiches: "buso_manga_larga_beiches.png",
                };
                
                const colorFile = colorMap[state.color];
                if (colorFile) {
                    return `${busoMangoBase}/${colorFile}`;
                }
            }

            // En pasos 1-2, mostrar frente/espalda según vistaPrenda
            return state.vistaPrenda === "trasera"
                ? `${busoMangoBase}/buso_manga_larga_de_espalda-removebg-preview.png`
                : `${busoMangoBase}/buso_manga_larga_de_frente-removebg-preview.png`;
        }

        const imageMap = {
            camiseta: {
                delantera: "/static/img/prendas/camisetas/Camisa_de_frente-removebg-preview.png",
                trasera: "/static/img/prendas/camisetas/Camisa_de_espalda-removebg-preview.png"
            },
            gorra: {
                delantera: "/static/img/prendas/gorras/gorra_de_frente-removebg-preview.png",
                trasera: "/static/img/prendas/gorras/gorra_de_espalda-removebg-preview.png"
            }
        };
        
        const productImages = imageMap[state.producto];
        if (productImages) {
            return productImages[state.vistaPrenda] || productImages.delantera;
        }
        return null;
    }

    function updateSummary() {
        const producto = productLabels[state.producto] || formatLabel(state.producto);
        const identidad = formatLabel(state.identidad);
        const tecnica = state.tecnica === "bordado" ? "Bordado" : "Impresion";
        const color = formatLabel(state.color);
        const estampado = state.estampado ? formatLabel(state.estampado) : "Pendiente";
        const talla = state.talla || "Pendiente";

        // Crear descripción completa con TODOS los pasos
        const descripcionCompleta = `${identidad} | ${tecnica} | ${producto} | ${color} | ${estampado} | ${talla}`;

        // Actualizar panel derecho (vista previa)
        if (productoInfoPreview) productoInfoPreview.textContent = producto;
        if (colorInfoPreview) colorInfoPreview.textContent = color;
        if (estampadoInfoPreview) estampadoInfoPreview.textContent = estampado;
        if (tallaInfoPreview) tallaInfoPreview.textContent = talla;
        if (precioInfoPreview) precioInfoPreview.textContent = priceMap[state.producto] || "$ 45.000";
        if (descripcionInfoPreview) descripcionInfoPreview.textContent = descripcionCompleta;
        
        // Actualizar identidad y técnica
        const identidadPreview = document.getElementById("preview-identidad");
        const tecnicaPreview = document.getElementById("preview-tecnica");
        if (identidadPreview) identidadPreview.textContent = identidad;
        if (tecnicaPreview) tecnicaPreview.textContent = tecnica;

        // Mostrar preview con imagen del producto o ícono
        const imagen = getProductImage();
        const icon = getProductIcon();
        
        if (imagen) {
            preview.innerHTML = `
                <div style="text-align: center; background: white; width: 100%; height: 100%;">
                    <img src="${imagen}" alt="${producto}" style="width: 200px; height: 250px; object-fit: contain; margin-bottom: 1rem;">
                    <p style="margin: 0.5rem 0; font-weight: bold;">${producto}</p>
                    <p style="margin: 0; font-size: 0.9rem; color: #666;">${identidad} | ${tecnica}</p>
                </div>
            `;
        } else {
            preview.innerHTML = `
                <div style="text-align: center;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">${icon}</div>
                    <p style="margin: 0.5rem 0; font-weight: bold;">${producto}</p>
                    <p style="margin: 0; font-size: 0.9rem; color: #666;">${identidad} | ${tecnica}</p>
                </div>
            `;
        }
    }

    function updateStepIndicators() {
        for (let i = 1; i <= 5; i += 1) {
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

    function validarPaso(paso) {
        switch(paso) {
            case 1:
                if (!state.nombre || !state.direccion || !state.correo || !state.telefono) {
                    alert("⚠️ Por favor completa todos los datos personales");
                    return false;
                }
                // Validar formato de correo
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(state.correo)) {
                    alert("⚠️ Por favor ingresa un correo válido");
                    return false;
                }
                if (!state.identidad || !state.tecnica) {
                    alert("⚠️ Por favor selecciona una Identidad Pública y una Técnica");
                    return false;
                }
                break;
            case 2:
                if (!state.producto) {
                    alert("⚠️ Por favor selecciona un Producto");
                    return false;
                }
                break;
            case 3:
                if (!state.color) {
                    alert("⚠️ Por favor selecciona un Color");
                    return false;
                }
                break;
            case 4:
                if (!state.estampado) {
                    alert("⚠️ Por favor selecciona un Estampado");
                    return false;
                }
                break;
            case 5:
                if (!state.talla) {
                    alert("⚠️ Por favor selecciona una Talla");
                    return false;
                }
                break;
        }
        return true;
    }

    function changeStep(step) {
        console.log(`📍 changeStep(${step}) - pasoActual: ${state.pasoActual} → ${step}`);
        document.querySelectorAll(".paso-contenido").forEach((section) => {
            section.classList.toggle("seccion-hidden", section.id !== `paso${step}`);
        });
        state.pasoActual = step;
        updateStepIndicators();
        updateSummary();
        updateTabsByProduct();
        updateVistaButtons();
        updatePanelLayout();
        
        // Validar el paso actual para habilitar/deshabilitar botones
        switch(step) {
            case 1:
                validarPaso1Realtime();
                break;
            case 2:
                validarPaso2Realtime();
                break;
            case 3:
                console.log("  → Estamos en paso 3 (COLOR), llamando updateColorAvailability()");
                updateColorAvailability();
                validarPaso3Realtime();
                break;
            case 4:
                validarPaso4Realtime();
                break;
            case 5:
                validarPaso5Realtime();
                break;
        }
    }

    function updatePanelLayout() {
        const panelDerecho = document.querySelector(".panel-derecho");
        const panelIzquierdo = document.querySelector(".panel-izquierdo");
        
        if (state.pasoActual === 1) {
            // En paso 1: ocultar panel derecho y centrar izquierdo
            if (panelDerecho) panelDerecho.style.display = "none";
            if (panelIzquierdo) {
                panelIzquierdo.style.maxWidth = "100%";
                panelIzquierdo.style.margin = "0 auto";
            }
        } else {
            // En pasos 2+: mostrar panel derecho con layout normal
            if (panelDerecho) panelDerecho.style.display = "block";
            if (panelIzquierdo) {
                panelIzquierdo.style.maxWidth = "";
                panelIzquierdo.style.margin = "";
            }
        }
    }

    function updateVistaButtons() {
        const botonesVistaDiv = document.getElementById("botones-vista-prenda");
        
        // Mostrar botones solo en paso 2 o superior (cuando ya se seleccionó producto)
        if (state.pasoActual >= 2) {
            botonesVistaDiv.style.display = "flex";
        } else {
            botonesVistaDiv.style.display = "none";
        }
    }

    function updateTabsByProduct() {
        const tabs = document.querySelectorAll("[data-area]");
        const barraAreas = document.querySelector(".barra-pestanas");
        let allowedAreas = [];
        let defaultActiveArea = null;
        
        // Prendas especiales que SOLO tienen impresion-delantera
        const prendasEspeciales = ["presillas", "rh", "pañoleta", "gorra", "contingencia", "gafete del nombre o apellido"];
        const esProductoEspecial = prendasEspeciales.some(p => p.toLowerCase() === state.producto.toLowerCase());

        // Si es prenda especial, solo mostrar impresion-delantera
        if (esProductoEspecial) {
            allowedAreas = ["impresion-delantera"];
            defaultActiveArea = "impresion-delantera";
        } else {
            // Para prendas normales (camiseta, buso, etc): pecho y mangas (SIN impresion-delantera)
            allowedAreas = [
                "pecho-izquierdo",
                "pecho-derecho",
                "manga-izquierda",
                "manga-derecha",
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

        // Habilitar todas las técnicas para todos los productos
        const tecnicaButtons = document.querySelectorAll("[data-tecnica]");
        tecnicaButtons.forEach((button) => {
            button.disabled = false;
            button.style.opacity = "1";
            button.style.cursor = "pointer";
        });
    }

    function updateTallaVisibility() {
        // Prendas que requieren selección de talla
        const prendasConTalla = ["camiseta", "buso", "buso-manga-larga"];
        const requiereTalla = prendasConTalla.some(p => p.toLowerCase() === state.producto.toLowerCase());
        
        const btnSiguiente = document.getElementById("btn-siguiente-paso5");
        const btnFinalizar = document.getElementById("btn-finalizar-paso5");
        
        if (requiereTalla) {
            // Mostrar botón que va al paso 6 (talla)
            if (btnSiguiente) btnSiguiente.style.display = "inline-block";
            if (btnFinalizar) btnFinalizar.style.display = "none";
        } else {
            // Mostrar botón que finaliza directamente (sin paso 6)
            if (btnSiguiente) btnSiguiente.style.display = "none";
            if (btnFinalizar) btnFinalizar.style.display = "inline-block";
        }
    }

    function updateColorAvailability() {
        // Obtener identidad actual de forma absolutamente segura
        const identidadActual = (state.identidad || "").toLowerCase().trim();
        const esEjercito = (identidadActual === "ejercito");
        
        console.log("🔄 updateColorAvailability ejecutado");
        console.log("✓ state.identidad:", state.identidad);
        console.log("✓ identidadActual:", identidadActual);
        console.log("✓ esEjercito:", esEjercito);
        console.log("✓ state.producto:", state.producto);
        
        // Si NO es Ejército: mostrar TODOS los colores, sin excepción
        if (!esEjercito) {
            console.log("→ NO es Ejército, mostrando TODOS los colores");
            document.querySelectorAll("[data-color]").forEach((button) => {
                button.style.display = "block";
                button.classList.remove("color-deshabilitado");
                button.style.opacity = "1";
                button.style.cursor = "pointer";
            });
            return; // Salida inmediata
        }
        
        console.log("→ ES Ejército, aplicando RESTRICCIONES");
        
        // ====== Si ES Ejército: aplicar restricciones ======
        const productName = (state.producto || "").toLowerCase();
        
        document.querySelectorAll("[data-color]").forEach((button) => {
            const color = button.dataset.color;
            
            // Paso 1: Determinar qué colores mostrar según el producto
            let mostrar = false;
            
            if (productName === "buso" || productName === "buso-manga-larga") {
                // Buso y Buso Manga Larga: mostrar 4 colores
                mostrar = ["blanco", "negro", "verde-claro", "beiches"].includes(color);
            } else if (["pañoleta", "gorra", "camiseta"].includes(productName)) {
                // Pañoleta, Gorra, Camiseta: mostrar 3 colores (sin blanco)
                mostrar = ["negro", "verde-claro", "beiches"].includes(color);
            } else {
                // Otros productos: mostrar todos
                mostrar = true;
            }
            
            button.style.display = mostrar ? "block" : "none";
            
            // Paso 2: Para Ejército, solo permitir usar verde y beiches
            const esUsable = ["verde-claro", "beiches"].includes(color);
            
            if (mostrar && esUsable) {
                button.classList.remove("color-deshabilitado");
                button.style.opacity = "1";
                button.style.cursor = "pointer";
            } else if (mostrar) {
                button.classList.add("color-deshabilitado");
                button.style.opacity = "0.5";
                button.style.cursor = "not-allowed";
            }
            
            console.log(`  - Color ${color}: mostrar=${mostrar}, usable=${esUsable}, opacity=${button.style.opacity}`);
        });
        
        // Paso 3: Si Ejército y color no permitido, cambiar a verde-claro
        if (!["verde-claro", "beiches"].includes(state.color)) {
            console.log("  - Cambiando color a verde-claro");
            state.color = "verde-claro";
            const btn = document.querySelector('[data-color="verde-claro"]');
            if (btn) {
                setActiveClass(
                    document.querySelectorAll("[data-color]"),
                    (el) => el === btn,
                    "seleccionada"
                );
                updateSummary();
            }
        }
    }

    function validarPaso1Realtime() {
        const nombre = document.getElementById("input-nombre").value.trim();
        const direccion = document.getElementById("input-direccion").value.trim();
        const correo = document.getElementById("input-correo").value.trim();
        const telefono = document.getElementById("input-telefono").value.trim();
        const btnSiguiente = document.getElementById("btn-siguiente-paso1");
        
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const emailValido = emailRegex.test(correo);
        
        const camposCompletos = nombre && direccion && correo && telefono && emailValido;
        
        if (btnSiguiente) {
            btnSiguiente.disabled = !camposCompletos;
            btnSiguiente.style.opacity = camposCompletos ? "1" : "0.5";
            btnSiguiente.style.cursor = camposCompletos ? "pointer" : "not-allowed";
        }
    }

    function validarPaso2Realtime() {
        const btnSiguiente = document.getElementById("btn-siguiente-paso2");
        const camposCompletos = state.producto;
        
        if (btnSiguiente) {
            btnSiguiente.disabled = !camposCompletos;
            btnSiguiente.style.opacity = camposCompletos ? "1" : "0.5";
            btnSiguiente.style.cursor = camposCompletos ? "pointer" : "not-allowed";
        }
    }

    function validarPaso3Realtime() {
        const btnSiguiente = document.getElementById("btn-siguiente-paso3");
        const camposCompletos = state.color;
        
        if (btnSiguiente) {
            btnSiguiente.disabled = !camposCompletos;
            btnSiguiente.style.opacity = camposCompletos ? "1" : "0.5";
            btnSiguiente.style.cursor = camposCompletos ? "pointer" : "not-allowed";
        }
    }

    function validarPaso4Realtime() {
        const btnSiguiente = document.getElementById("btn-siguiente-paso4");
        const camposCompletos = state.estampado;
        
        if (btnSiguiente) {
            btnSiguiente.disabled = !camposCompletos;
            btnSiguiente.style.opacity = camposCompletos ? "1" : "0.5";
            btnSiguiente.style.cursor = camposCompletos ? "pointer" : "not-allowed";
        }
    }

    function validarPaso5Realtime() {
        const btnFinalizar = document.getElementById("btn-finalizar-paso5");
        const camposCompletos = state.talla;
        
        if (btnFinalizar) {
            btnFinalizar.disabled = !camposCompletos;
            btnFinalizar.style.opacity = camposCompletos ? "1" : "0.5";
            btnFinalizar.style.cursor = camposCompletos ? "pointer" : "not-allowed";
        }
    }

    function bindSelections() {
        // Validación en tiempo real para paso 1
        const inputNombre = document.getElementById("input-nombre");
        const inputDireccion = document.getElementById("input-direccion");
        const inputCorreo = document.getElementById("input-correo");
        const inputTelefono = document.getElementById("input-telefono");
        const btnSiguientePaso1 = document.getElementById("btn-siguiente-paso1");
        
        if (inputNombre) inputNombre.addEventListener("input", validarPaso1Realtime);
        if (inputDireccion) inputDireccion.addEventListener("input", validarPaso1Realtime);
        if (inputCorreo) inputCorreo.addEventListener("input", validarPaso1Realtime);
        if (inputTelefono) inputTelefono.addEventListener("input", validarPaso1Realtime);
        
        // Desabilitar el botón inicialmente
        if (btnSiguientePaso1) {
            btnSiguientePaso1.disabled = true;
            btnSiguientePaso1.style.opacity = "0.5";
            btnSiguientePaso1.style.cursor = "not-allowed";
        }
        
        // Manejar captura de datos personales en paso 1
        if (btnSiguientePaso1) {
            btnSiguientePaso1.addEventListener("click", () => {
                state.nombre = document.getElementById("input-nombre").value;
                state.direccion = document.getElementById("input-direccion").value;
                state.correo = document.getElementById("input-correo").value;
                state.telefono = document.getElementById("input-telefono").value;
                
                if (validarPaso(1)) {
                    changeStep(2);
                }
            });
        }

        // Manejar selección de identidad pública
        document.querySelectorAll("[data-opcion]").forEach((button) => {
            button.addEventListener("click", () => {
                console.log("🔘 Clic en botón de identidad");
                console.log("   data-opcion:", button.dataset.opcion);
                state.identidad = button.dataset.opcion;
                console.log("   state.identidad ACTUALIZADO a:", state.identidad);
                setActiveClass(
                    document.querySelectorAll("[data-opcion]"),
                    (element) => element === button,
                    "activo"
                );
                console.log("   Llamando updateColorAvailability()");
                updateColorAvailability();
                updateSummary();
                validarPaso2Realtime();
            });
        });

        document.querySelectorAll("[data-producto]").forEach((button) => {
            button.addEventListener("click", () => {
                state.producto = button.dataset.producto;
                setActiveClass(
                    document.querySelectorAll("[data-producto]"),
                    (element) => element === button,
                    "seleccionada"
                );
                updateTabsByProduct();
                updateTallaVisibility();
                updateColorAvailability();
                updateSummary();
                validarPaso3Realtime();
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
                validarPaso2Realtime();
            });
        });

        document.querySelectorAll("[data-color]").forEach((button) => {
            button.addEventListener("click", () => {
                // No permitir seleccionar colores deshabilitados
                if (button.classList.contains("color-deshabilitado")) {
                    console.log("⚠️ Intento de seleccionar color deshabilitado:", button.dataset.color);
                    return;
                }
                
                state.color = button.dataset.color;
                setActiveClass(
                    document.querySelectorAll("[data-color]"),
                    (element) => element === button,
                    "seleccionada"
                );
                updateSummary();
                validarPaso4Realtime();
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
                validarPaso5Realtime();
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
                validarPaso6Realtime();
            });
        });

        // Botones de vista delantera/trasera
        document.querySelectorAll(".btn-vista-prenda").forEach((button) => {
            button.addEventListener("click", () => {
                state.vistaPrenda = button.dataset.vista;
                setActiveClass(
                    document.querySelectorAll(".btn-vista-prenda"),
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

        document.getElementById("btn-finalizar-paso4")?.addEventListener("click", () => {
            updateSummary();
            alert("La configuracion quedo lista. El siguiente paso sera conectarla al flujo real de carrito.");
        });

        // Botones de navegación Siguiente/Atrás
        document.getElementById("btn-siguiente-paso2")?.addEventListener("click", () => {
            if (validarPaso(2)) changeStep(3);
        });

        // Deshabilitar botón Atrás en paso 1 (es el primer paso)
        const btnAtrasPaso1 = document.getElementById("btn-atras-paso1");
        if (btnAtrasPaso1) {
            btnAtrasPaso1.disabled = true;
            btnAtrasPaso1.style.opacity = "0.5";
            btnAtrasPaso1.style.cursor = "not-allowed";
        }

        document.getElementById("btn-atras-paso2")?.addEventListener("click", () => {
            changeStep(1);
        });

        document.getElementById("btn-siguiente-paso3")?.addEventListener("click", () => {
            if (validarPaso(3)) changeStep(4);
        });

        document.getElementById("btn-atras-paso3")?.addEventListener("click", () => {
            changeStep(2);
        });

        document.getElementById("btn-siguiente-paso4")?.addEventListener("click", () => {
            if (validarPaso(4)) changeStep(5);
        });

        document.getElementById("btn-atras-paso4")?.addEventListener("click", () => {
            changeStep(3);
        });

        document.getElementById("btn-atras-paso5")?.addEventListener("click", () => {
            changeStep(4);
        });

        document.getElementById("btn-finalizar-paso5")?.addEventListener("click", () => {
            if (validarPaso(5)) {
                updateSummary();
                alert("✅ Personalización completada. Resumen:\n\nNombre: " + state.nombre + "\nDirección: " + state.direccion + "\nCorreo: " + state.correo + "\nTeléfono: " + state.telefono + "\n\nIdentidad: " + formatLabel(state.identidad) + "\nTécnica: " + (state.tecnica === "bordado" ? "Bordado" : "Impresion") + "\nProducto: " + (productLabels[state.producto] || formatLabel(state.producto)) + "\nColor: " + formatLabel(state.color) + "\nEstampado: " + (state.estampado ? formatLabel(state.estampado) : "Ninguno") + "\nTalla: " + state.talla);
            }
        });

        // Botón Atrás en el panel derecho
        document.getElementById("btn-atras-panel")?.addEventListener("click", () => {
            if (state.pasoActual > 1) {
                changeStep(state.pasoActual - 1);
            } else {
                alert("⚠️ Ya estás en el primer paso");
            }
        });

        // Botón Agregar al Carrito
        document.getElementById("btn-agregar-carrito")?.addEventListener("click", () => {
            if (validarPaso(6)) {
                const producto = productLabels[state.producto] || formatLabel(state.producto);
                const identidad = formatLabel(state.identidad);
                const tecnica = state.tecnica === "bordado" ? "Bordado" : "Impresion";
                const color = formatLabel(state.color);
                const estampado = state.estampado ? formatLabel(state.estampado) : "Ninguno";
                const talla = state.talla || "Sin talla";
                
                alert(`✅ Producto agregado al carrito:\n\nNombre: ${state.nombre}\nDirección: ${state.direccion}\nCorreo: ${state.correo}\nTeléfono: ${state.telefono}\n\n${producto}\nIdentidad: ${identidad}\nTécnica: ${tecnica}\nColor: ${color}\nEstampado: ${estampado}\nTalla: ${talla}\nPrecio: ${priceMap[state.producto] || "$ 45.000"}`);
            } else {
                alert("⚠️ Por favor completa todos los campos antes de agregar al carrito");
            }
        });

        // Hacer clickeables los números de paso
        for (let i = 1; i <= 5; i++) {
            const stepHeader = document.getElementById(`paso${i}-header`);
            if (stepHeader) {
                stepHeader.style.cursor = "pointer";
                stepHeader.addEventListener("click", () => {
                    changeStep(i);
                });
                // Hacer el contenedor del paso también clickeable
                const stepContainer = stepHeader.parentElement;
                if (stepContainer) {
                    stepContainer.style.cursor = "pointer";
                    stepContainer.addEventListener("click", () => {
                        changeStep(i);
                    });
                }
            }
        }
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
    updateTallaVisibility();
    updateColorAvailability();
    updateStepIndicators();
    updateSummary();
    changeStep(state.pasoActual); // Inicializar visibilidad de botones y preview
})();
