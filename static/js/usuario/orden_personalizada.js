(function () {
    const state = {
        // Datos personales
        nombre: "",
        rango: "",
        direccion: "",
        correo: "",
        telefono: "",
        // Configuración de la prenda
        genero: "unisex",
        identidad: "policia",
        producto: "",
        tecnica: "bordado",
        color: "",
        estampado: "",
        talla: null,
        pasoActual: 1,
        vistaPrenda: "delantera",
    };

    const priceMap = {
        camiseta: "$ 45.000",
        buso: "$ 78.000",
        gorra: "$ 35.000",
        pañoleta: "$ 28.000",
        panoleta: "$ 28.000",
        "buso-manga-larga": "$ 85.000",
        "buso_tactico": "$ 95.000",
        "buso tactico": "$ 95.000",
        presillas: "$ 15.000",
        rh: "$ 12.000",
    };

    const productLabels = {
        camiseta: "Camiseta",
        buso: "Buso",
        gorra: "Gorra",
        pañoleta: "Pañoleta",
        panoleta: "Pañoleta",
        "buso-manga-larga": "Buso manga larga",
        "buso_tactico": "Buso Táctico",
        "buso tactico": "Buso Táctico",
        presillas: "Presillas",
        rh: "Rh",
    };

    // Elementos del panel derecho (vista previa) - NUEVOS IDs
    const productoInfoPreview = document.getElementById("preview-producto");
    const descripcionInfoPreview = document.getElementById("preview-descripcion");
    const colorInfoPreview = document.getElementById("preview-color");
    const estampadoInfoPreview = document.getElementById("preview-estampado");
    const tallaInfoPreview = document.getElementById("preview-talla");
    const precioInfoPreview = document.getElementById("preview-precio");
    const btnVistaDelantera = document.getElementById("btn-vista-delantera");
    const btnVistaTrasera = document.getElementById("btn-vista-trasera");
    
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
            panoleta: "🧣",
            "buso-manga-larga": "👚",
            "buso_tactico": "🪖",
            "buso tactico": "🪖",
            presillas: "📌",
            rh: "🩸",
        };
        
        return iconMap[state.producto] || "👕";
    }

    function getProductImage() {
        const productName = (state.producto || "").toLowerCase().trim();
        const isBack = state.vistaPrenda === "trasera";
        const identidad = (state.identidad || "").toLowerCase().trim();
        
        // BUSO
        if (productName === "buso") {
            if (identidad === "ejercito") {
                return isBack 
                    ? "/static/img/prendas/ejercito/buso/Buso_de_espalda_-removebg-preview.png"
                    : "/static/img/prendas/ejercito/buso/Buso_de_frente-removebg-preview.png";
            } else if (identidad === "gaula") {
                return isBack 
                    ? "/static/img/prendas/gaula/buso/espalda_gaula.png"
                    : "/static/img/prendas/gaula/buso/defrente_gaula.png";
            } else if (identidad === "policia") {
                return isBack 
                    ? "/static/img/prendas/Policia/buso/espalda_policia.png"
                    : "/static/img/prendas/Policia/buso/defrente_policia.png";
            }
        }

        // BUSO MANGA LARGA
        if (productName === "buso-manga-larga" || productName === "buso_manga_larga" || productName === "buso manga larga") {
            if (identidad === "ejercito") {
                return isBack 
                    ? "/static/img/prendas/ejercito/buso-manga-larga/buso_manga_larga_de_espalda-removebg-preview.png"
                    : "/static/img/prendas/ejercito/buso-manga-larga/buso_manga_larga_de_frente-removebg-preview.png";
            } else if (identidad === "gaula") {
                return isBack 
                    ? "/static/img/prendas/gaula/buso_manga_larga/detras_gaula.png"
                    : "/static/img/prendas/gaula/buso_manga_larga/manga_larga_gaula.png";
            } else if (identidad === "policia") {
                return isBack 
                    ? "/static/img/prendas/Policia/buso_manga_larga/detras_policia.png"
                    : "/static/img/prendas/Policia/buso_manga_larga/frente_poli.png";
            }
        }

        // BUSO TÁCTICO
        if (productName === "buso_tactico" || productName === "buso tactico") {
            if (identidad === "ejercito") {
                return isBack 
                    ? "/static/img/prendas/ejercito/buso_tactico/buso_manga_larga_de_espalda-removebg-preview.png"
                    : "/static/img/prendas/ejercito/buso_tactico/buso_manga_larga_de_frente-removebg-preview.png";
            } else if (identidad === "gaula") {
                return isBack 
                    ? "/static/img/prendas/gaula/buso_tactico/detras-tactico.png"
                    : "/static/img/prendas/gaula/buso_tactico/frente-tactico.png";
            } else if (identidad === "policia") {
                return isBack 
                    ? "/static/img/prendas/Policia/buso_tactico/detras_policia.png"
                    : "/static/img/prendas/Policia/buso_tactico/frente-poli.png";
            }
        }
        
        // CAMISETA / GUERRERA
        if (productName === "camiseta" || productName === "guerrera") {
            if (identidad === "ejercito") {
                return isBack 
                    ? "/static/img/prendas/ejercito/guerreras/Camisa_de_espalda-removebg-preview.png"
                    : "/static/img/prendas/ejercito/guerreras/Camisa_de_frente-removebg-preview.png";
            } else if (identidad === "gaula") {
                return isBack 
                    ? "/static/img/prendas/gaula/guerrera/guerrera-espaldar.png"
                    : "/static/img/prendas/gaula/guerrera/guerrera-frente.png";
            } else if (identidad === "policia") {
                return isBack 
                    ? "/static/img/prendas/Policia/guerra/camisa_de_espalda_policia.png"
                    : "/static/img/prendas/Policia/guerra/Camisa_de_frente-policia.png";
            }
        }
        
        // GORRA
        if (productName === "gorra") {
            if (identidad === "ejercito") {
                return isBack 
                    ? "/static/img/prendas/ejercito/gorras/gorra_de_espalda-removebg-preview.png"
                    : "/static/img/prendas/ejercito/gorras/gorra_de_frente-removebg-preview.png";
            } else if (identidad === "gaula") {
                return isBack 
                    ? "/static/img/prendas/gaula/gorras/gorra_de_espalda-gaula.png"
                    : "/static/img/prendas/gaula/gorras/gorra_de_frente-rgaula.png";
            } else if (identidad === "policia") {
                return isBack 
                    ? "/static/img/prendas/Policia/gorras/gorra_de_espalda-gaula.png"
                    : "/static/img/prendas/Policia/gorras/gorra_de_frente-rgaula.png";
            }
        }
        
        // PAÑOLETA
        if (productName === "pañoleta" || productName === "panoleta") {
            if (identidad === "ejercito") {
                return isBack 
                    ? "/static/img/prendas/ejercito/pañoletas/panoleta_espalda.png"
                    : "/static/img/prendas/ejercito/pañoletas/panoleta_frente.png";
            } else if (identidad === "gaula") {
                return isBack 
                    ? "/static/img/prendas/gaula/Pañoletas/panoleta_espalda_gaula.png"
                    : "/static/img/prendas/gaula/Pañoletas/panoleta_frente_gaula.png";
            } else if (identidad === "policia") {
                return isBack 
                    ? "/static/img/prendas/Policia/pañoletas/panoleta_espalda_gaula.png"
                    : "/static/img/prendas/Policia/pañoletas/panoleta_frente_gaula.png";
            }
        }
        
        // RH
        if (productName === "rh") {
            if (identidad === "ejercito") {
                return isBack 
                    ? "/static/img/prendas/ejercito/Rh/rh_espaldar.png"
                    : "/static/img/prendas/ejercito/Rh/rh_defrente.png";
            } else if (identidad === "gaula") {
                return isBack 
                    ? "/static/img/prendas/gaula/Rh/rh_espaldar.png"
                    : "/static/img/prendas/gaula/Rh/rh_defrente.png";
            } else if (identidad === "policia") {
                return isBack 
                    ? "/static/img/prendas/Policia/Rh/rh_espaldar.png"
                    : "/static/img/prendas/Policia/Rh/rh-defrente.png";
            }
        }
        
        // PRESILLAS
        if (productName === "presillas") {
            if (identidad === "ejercito") {
                return "/static/img/prendas/ejercito/presillas/presilla_ejercito.png";
            } else if (identidad === "gaula") {
                return "/static/img/prendas/gaula/presillas/presilla_gaula.png";
            } else if (identidad === "policia") {
                return "/static/img/prendas/Policia/presillas/presilla_policia.png";
            }
        }

        // GAFETE
        if (productName.includes("gafete")) {
            if (identidad.includes("ejercito")) {
                return isBack 
                    ? "/static/img/prendas/ejercito/gafete%20del%20nombre%20o%20apellido/reves-gafete.png"
                    : "/static/img/prendas/ejercito/gafete%20del%20nombre%20o%20apellido/frente.png";
            } else if (identidad.includes("gaula")) {
                return isBack 
                    ? "/static/img/prendas/gaula/gafete%20del%20nombre%20o%20apellido/reves-gafete.png"
                    : "/static/img/prendas/gaula/gafete%20del%20nombre%20o%20apellido/frente.png";
            } else if (identidad.includes("policia")) {
                return isBack 
                    ? "/static/img/prendas/Policia/gafete%20del%20nombre%20o%20apellido/respalda-gafete.png"
                    : "/static/img/prendas/Policia/gafete%20del%20nombre%20o%20apellido/frente-gafete.png";
            }
        }
        return null;
    }

    // Función para obtener la imagen de prenda con color específico (para Paso 3)
    function getProductColorImage(color) {
        const productName = (state.producto || "").toLowerCase();
        const identidad = (state.identidad || "").toLowerCase();
        const isBack = state.vistaPrenda === "trasera";
        
        // Mapeo de colores a nombres de archivos
        const colorMap = {
            blanco: "blanco",
            negro: "negro",
            "verde-claro": "verde",
            beiches: "beiches",
            dorado: "dorado",
            cafe: "cafe",
            "azul-noche": "azul-noche"
        };
        
        const colorName = colorMap[color] || color;
        
        // BUSO
        if (productName === "buso") {
            if (identidad === "ejercito") return `/static/img/prendas/ejercito/buso/buso_${colorName}.png`;
            if (identidad === "policia") return `/static/img/prendas/Policia/buso/buso_${colorName === 'azul-noche' ? 'azul' : colorName}.png`;
            if (identidad === "gaula") return `/static/img/prendas/gaula/buso/buso_${colorName}.png`;
        }

        // BUSO MANGA LARGA
        if (productName === "buso-manga-larga" || productName === "buso_manga_larga" || productName === "buso manga larga") {
            if (identidad === "ejercito") return `/static/img/prendas/ejercito/buso-manga-larga/buso_manga_larga_${colorName}.png`;
            if (identidad === "policia") return `/static/img/prendas/Policia/buso_manga_larga/buso${colorName === 'azul-noche' ? '-poli' : (colorName === 'verde' ? '_poli' : '-' + colorName)}.png`;
            if (identidad === "gaula") return `/static/img/prendas/gaula/buso_manga_larga/buso_manga_larga_${colorName}.png`;
        }

        // BUSO TÁCTICO
        if (productName === "buso_tactico" || productName === "buso tactico" || productName === "buso-tactico") {
            if (identidad === "ejercito") return `/static/img/prendas/ejercito/buso_tactico/camisa_${colorName}.png`;
            if (identidad === "policia") return `/static/img/prendas/Policia/buso_tactico/tactico${colorName === 'azul-noche' ? '-poli' : ''}.png`;
            if (identidad === "gaula") return `/static/img/prendas/gaula/buso_tactico/${colorName}.png`;
        }

        // CAMISETA / GUERRERA
        if (productName === "camiseta" || productName === "guerrera") {
            if (identidad === "ejercito") return `/static/img/prendas/ejercito/camisetas/camisa_${colorName}.png`;
            if (identidad === "policia") {
                if (productName === "guerrera") return `/static/img/prendas/Policia/guerra/guerrera_${colorName === 'azul-noche' ? 'policia' : (colorName === 'verde' ? 'poli' : colorName)}.png`;
                return isBack ? `/static/img/prendas/Policia/guerra/camisa_de_espalda_policia.png` : `/static/img/prendas/Policia/guerra/Camisa_de_frente-policia.png`;
            }
            if (identidad === "gaula") return `/static/img/prendas/gaula/guerrera/guerrera_${colorName}.png`;
        }

        // GORRA
        if (productName === "gorra") {
            if (color === "blanco") return null; // Sin blanco
            if (identidad === "ejercito") return `/static/img/prendas/ejercito/gorras/gorra_${colorName}.png`;
            if (identidad === "policia") return `/static/img/prendas/Policia/gorras/gorra_${colorName === 'azul-noche' ? 'azul' : colorName}.png`;
            if (identidad === "gaula") return `/static/img/prendas/gaula/gorras/gorra_${colorName}.png`;
        }

        // PAÑOLETA
        if (productName === "pañoleta" || productName === "panoleta") {
            if (identidad === "ejercito") return `/static/img/prendas/ejercito/pañoletas/panoleta_${colorName}.png`;
            if (identidad === "policia") {
                if (colorName === 'azul-noche') return `/static/img/prendas/Policia/pañoletas/pañoleta-azul.png`;
                return `/static/img/prendas/Policia/pañoletas/panoleta_${colorName}.png`;
            }
        }
        
        // RH
        if (productName === "rh") {
            if (identidad === "ejercito") return `/static/img/prendas/ejercito/Rh/rh_${colorName}.png`;
            if (identidad === "policia") return `/static/img/prendas/Policia/Rh/rh_${colorName === 'azul-noche' ? 'azul' : colorName}.png`;
            if (identidad === "gaula") return `/static/img/prendas/gaula/Rh/rh_${colorName}.png`;
        }
        
        // GAFETE
        if (productName.includes("gafete")) {
            if (identidad === "policia") {
                return `/static/img/prendas/Policia/gafete%20del%20nombre%20o%20apellido/${colorName === 'azul-noche' ? 'azul' : 'verde'}-gafete.png`;
            }
            return null; // Otras fuerzas no tienen gafete coloreado
        }
        
        return null;
    }

    function getColorHex(colorName) {
        // Mapeo de nombres de color a códigos hexadecimales
        const colorHexMap = {
            blanco: "#ffffff",
            negro: "#000000",
            "verde-claro": "#2D5016",
            beiches: "#D3C0A3",
            dorado: "#e6f141",
            cafe: "#424215",
            "azul-noche": "#192857"
        };
        return colorHexMap[colorName] || "#cccccc";
    }

    function updateSummary() {
        const producto = productLabels[state.producto] || formatLabel(state.producto);
        const identidad = formatLabel(state.identidad);
        const tecnica = state.tecnica === "bordado" ? "Bordado" : "Impresión";
        const color = formatLabel(state.color);
        const estampado = state.estampado ? formatLabel(state.estampado) : "Pendiente";
        const talla = state.talla || "Pendiente";

        // Crear descripción completa con TODOS los pasos
        const descripcionCompleta = `${identidad} | ${tecnica} | ${producto} | ${color} | ${estampado} | ${talla}`;

        // Actualizar panel derecho (vista previa)
        if (productoInfoPreview) productoInfoPreview.textContent = producto;
        
        // Mostrar color con cuadro de color
        if (colorInfoPreview) {
            if (state.pasoActual === 3 || state.pasoActual === 4 || state.pasoActual === 5) {
                const colorHex = getColorHex(state.color);
                colorInfoPreview.innerHTML = `
                    <span style="display: inline-flex; align-items: center; gap: 0.5rem;">
                        <span style="display: inline-block; width: 20px; height: 20px; border-radius: 3px; border: 1px solid #999; background-color: ${colorHex};"></span>
                        ${color}
                    </span>
                `;
            } else {
                colorInfoPreview.textContent = color;
            }
        }
        
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
        // En Paso 3 o superior, mostrar la imagen con el color seleccionado
        let imagen = null;
        if (state.pasoActual >= 3) {
            imagen = getProductColorImage(state.color);
        }
        
        // Si no hay imagen de color, usar la imagen base
        if (!imagen) {
            imagen = getProductImage();
        }
        
        const icon = getProductIcon();
        
        if (imagen) {
            // Aumentar un poco el tamaño si es un accesorio pequeño como Gafetes, RH o Presillas
            let scaleStyle = "";
            const isGafete = state.producto === "gafete del nombre o apellido" || state.producto === "gafete";
            const isSmallItem = state.producto === "rh" || state.producto === "presillas";
            
            if (isGafete) {
                scaleStyle = "transform: scale(2.2);";
            } else if (isSmallItem) {
                scaleStyle = "transform: scale(1.6);";
            }

            let existingContainer = preview.querySelector("#preview-container");
            
            if (!existingContainer) {
                preview.innerHTML = `
                    <div id="preview-container" style="position: relative; text-align: center; background: white; width: 100%; height: 300px; display: flex; justify-content: center; align-items: center; overflow: hidden; border-radius: 8px;">
                        <img id="imagen-producto" src="" alt="Vista Previa" style="width: 100%; height: 100%; max-width: 260px; max-height: 260px; object-fit: contain; transition: transform 0.2s ease-in-out; z-index: 1;">
                        <div id="gafete-overlay" style="display: none; position: absolute; top: 40%; left: 50%; transform: translate(-50%, -50%) scale(2.2); text-align: center; color: #ccff00; font-family: 'Arial Rounded MT Bold', 'Helvetica Rounded', Arial, sans-serif; white-space: nowrap; z-index: 5; display: flex; flex-direction: column; align-items: center; justify-content: center; letter-spacing: 0.5px;">
                            <div id="overlay-rango" style="font-size: 11px; font-weight: 800; text-shadow: -1px -1px 0 #0d1b2a, 1px -1px 0 #0d1b2a, -1px 1px 0 #0d1b2a, 1px 1px 0 #0d1b2a; margin-bottom: -1px;"></div>
                            <div id="overlay-nombre" style="font-size: 11px; font-weight: 900; text-shadow: -1px -1px 0 #0d1b2a, 1px -1px 0 #0d1b2a, -1px 1px 0 #0d1b2a, 1px 1px 0 #0d1b2a; text-transform: uppercase;"></div>
                        </div>
                    </div>
                `;
            }
            
            let imgEl = preview.querySelector("#imagen-producto");
            imgEl.src = imagen;
            imgEl.alt = state.producto || 'Vista Previa de Prenda';
            if (isGafete) { imgEl.style.transform = "scale(2.2)"; } else if (isSmallItem) { imgEl.style.transform = "scale(1.6)"; } else { imgEl.style.transform = "none"; }
            
            let overlayEl = preview.querySelector("#gafete-overlay");
            if (isGafete && state.vistaPrenda !== "trasera") {
                overlayEl.style.display = "flex";
                
                // Determinar colores basados en la selección o en la imagen mostrada
                let textColor = "#ccff00"; // Neon green por defecto
                let shadowColor = "#0d1b2a"; // Sombra oscura azulada/negra por defecto
                
                // Si la imagen es la versión "verde", o el color seleccionado es verde-claro
                if ((imagen && imagen.includes("verde")) || state.color === "verde-claro") {
                    textColor = "#d0d6c0"; // Blanco hueso / verde muy claro (del parche verde)
                    shadowColor = "#394524"; // Sombra verde oliva oscuro
                } else if ((imagen && (imagen.includes("azul") || imagen.includes("negro"))) || state.color === "azul-noche" || state.color === "negro") {
                    textColor = "#ccff00"; // Neon green
                    shadowColor = "#0d1b2a"; // Sombra negra/azul oscuro
                } else if (!state.color && state.identidad === "policia") {
                    // Si aún no se ha seleccionado color (Paso 2), forzaremos el visual de la imagen default
                    if (imagen && imagen.includes("frente-gafete")) {
                        textColor = "#d0d6c0"; 
                        shadowColor = "#394524";
                    }
                } else if (state.color === "blanco") {
                    textColor = "#000000"; 
                    shadowColor = "#ffffff";
                }

                overlayEl.style.color = textColor;
                const shadowVal = `-1px -1px 0 ${shadowColor}, 1px -1px 0 ${shadowColor}, -1px 1px 0 ${shadowColor}, 1px 1px 0 ${shadowColor}`;
                preview.querySelector("#overlay-rango").style.textShadow = shadowVal;
                preview.querySelector("#overlay-nombre").style.textShadow = shadowVal;
                
                const rangoFinal = state.rango ? state.rango.charAt(0).toUpperCase() + state.rango.slice(1).toLowerCase() : 'Rango';
                const nombreFinal = state.nombre ? state.nombre.toUpperCase() : 'NOMBRE';
                
                preview.querySelector("#overlay-rango").textContent = rangoFinal;
                preview.querySelector("#overlay-nombre").textContent = nombreFinal;
            } else {
                overlayEl.style.display = "none";
            }
        } else {
            let iconClass = getProductIcon() || "fa-palette";
            preview.innerHTML = `
                <div style="text-align: center;">
                    <i class="fas ${iconClass}" style="font-size: 3rem; margin-bottom: 1rem; color: #555;"></i>
                    <p style="color: #666;">Selecciona opciones para tu prenda</p>
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
                if (!state.nombre || !state.rango || !state.direccion || !state.correo || !state.telefono) {
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
        state.pasoActual = step;
        
        // ⚠️ Actualizar Layout PRIMERO (para evitar que cualquier error detenga esto)
        updatePanelLayout();
        
        document.querySelectorAll(".paso-contenido").forEach((section) => {
            section.classList.toggle("seccion-hidden", section.id !== `paso${step}`);
        });
        
        updateStepIndicators();
        updateSummary();
        updateTabsByProduct();
        updateEstampados();
        updateVistaButtons();
        
        // Validar el paso actual para habilitar/deshabilitar botones
        try {
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
        } catch(error) {
            console.error("Error en validación de paso:", error);
        }
    }


    function updatePanelLayout() {
        const panelDerecho = document.getElementById("panel-vista-previa");
        if (!panelDerecho) return;
        
        console.log("==> updatePanelLayout(), pasoActual:", state.pasoActual);

        if (state.pasoActual === 1) {
            panelDerecho.style.display = "none";
        } else {
            panelDerecho.style.display = "flex";
        }
    }

    function updateVistaButtons() {
        const controlesVista = document.querySelector(".controles-vista-previa");
        if (controlesVista) {
            // Mostrar botones solo en paso 2
            if (state.pasoActual === 2) {
                controlesVista.style.display = "flex";
            } else {
                controlesVista.style.display = "none";
            }
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
        const btnSiguiente = document.getElementById("btn-siguiente-paso4");
        
        // Siempre mostrar botón que va al paso 5 (talla)
        if (btnSiguiente) btnSiguiente.style.display = "inline-block";
    }

    function updateEstampados() {
        const identidad = state.identidad ? state.identidad.toLowerCase().trim() : "policia";
        
        // Mapeo dinámico para todos los estampados
        const estampadosTipos = ['escudos', 'nombres', 'distintivos', 'parches'];
        
        estampadosTipos.forEach(tipo => {
            const btn = document.querySelector(`[data-estampado="${tipo}"]`);
            if (btn) {
                const muestra = btn.querySelector('.muestra-color');
                if (muestra) {
                    let imgFolderUrl = "";
                    
                    // Capitalizar la primera letra del tipo para que coincida con la carpeta de forma exacta (Ej: Escudos, Nombres)
                    const carpetaTipo = tipo.charAt(0).toUpperCase() + tipo.slice(1);
                    
                    if (identidad === "ejercito") {
                        if (tipo === "escudos") imgFolderUrl = `url('/static/img/estampados/ejercito/${carpetaTipo}/ejercito.png')`;
                        else if (tipo === "nombres") imgFolderUrl = `url('/static/img/estampados/ejercito/${carpetaTipo}/nombre.png')`; // Ajusta el nombre si difiere
                        else if (tipo === "distintivos") imgFolderUrl = `url('/static/img/estampados/ejercito/${carpetaTipo}/distintivo.png')`;
                        else if (tipo === "parches") imgFolderUrl = `url('/static/img/estampados/ejercito/${carpetaTipo}/parche.png')`;
                    } else if (identidad === "gaula") {
                        if (tipo === "escudos") imgFolderUrl = `url('/static/img/estampados/gaula/${carpetaTipo}/gaula.png')`;
                        else if (tipo === "nombres") imgFolderUrl = `url('/static/img/estampados/gaula/${carpetaTipo}/nombre.png')`;
                        else if (tipo === "distintivos") imgFolderUrl = `url('/static/img/estampados/gaula/${carpetaTipo}/distintivo.png')`;
                        else if (tipo === "parches") imgFolderUrl = `url('/static/img/estampados/gaula/${carpetaTipo}/parche.png')`;
                    } else { // Policia
                        if (tipo === "escudos") imgFolderUrl = `url('/static/img/estampados/policia/${carpetaTipo}/policia.png')`;
                        else if (tipo === "nombres") imgFolderUrl = `url('/static/img/estampados/policia/${carpetaTipo}/nombre.png')`;
                        else if (tipo === "distintivos") imgFolderUrl = `url('/static/img/estampados/policia/${carpetaTipo}/distintivo.png')`;
                        else if (tipo === "parches") imgFolderUrl = `url('/static/img/estampados/policia/${carpetaTipo}/parche_policia.png')`;
                    }
                    
                    // Solo actualizamos a la imagen si no da fallback vacío o fallback manual de ser necesario.
                    // Para evitar errores 404, si la imagen no existe simplemente que quede la estructura, pero lo solicitaste para "las fuerzas y todos [los estampados]"
                    muestra.style.backgroundImage = imgFolderUrl;
                    muestra.style.backgroundPosition = "center";
                    muestra.style.backgroundSize = "contain";
                    muestra.style.backgroundRepeat = "no-repeat";
                    muestra.style.backgroundColor = "transparent";
                }
            }
        });
    }

    function updateColorAvailability() {
        // Matriz de colores permitidos por FUERZA y PRODUCTO
        const colorMatriz = {
            "ejercito": {
                "buso": ["negro", "verde-claro", "blanco", "beiches"],
                "buso-tactico": ["verde-claro", "beiches", "negro"],
                "buso_tactico": ["verde-claro", "beiches", "negro"],
                "buso-manga-larga": ["beiches", "blanco", "negro", "verde-claro"],
                "camiseta": ["verde-claro", "beiches"],
                "gafete": ["dorado", "verde-claro"],
                "gorra": ["negro", "verde-claro", "beiches"],
                "pañoleta": ["verde-claro", "negro", "beiches"],
                "presillas": ["dorado", "verde-claro"],
                "rh": ["verde-claro", "cafe"]
            },
            "policia": {
                "buso": ["verde-claro", "azul-noche", "negro"],
                "buso-tactico": ["verde-claro", "azul-noche"],
                "buso_tactico": ["verde-claro", "azul-noche"],
                "buso-manga-larga": ["verde-claro", "azul-noche", "negro"],
                "camiseta": ["verde-claro", "azul-noche"],
                "guerrera": ["verde-claro", "azul-noche"],
                "gafete": ["verde-claro", "azul-noche"],
                "gafete del nombre o apellido": ["verde-claro", "azul-noche"],
                "gorra": ["verde-claro", "azul-noche"],
                "pañoleta": ["verde-claro", "negro", "azul-noche"],
                "presillas": ["dorado", "azul-noche"],
                "rh": ["verde-claro", "azul-noche"]
            },
            "gaula": {
                "buso": ["blanco", "negro", "verde-claro", "beiches", "dorado", "cafe", "azul-noche"],
                "buso-tactico": ["blanco", "negro", "verde-claro", "beiches", "dorado", "cafe", "azul-noche"],
                "buso_tactico": ["blanco", "negro", "verde-claro", "beiches", "dorado", "cafe", "azul-noche"],
                "buso-manga-larga": ["blanco", "negro", "verde-claro", "beiches", "dorado", "cafe", "azul-noche"],
                "camiseta": ["blanco", "negro", "verde-claro", "beiches", "dorado", "cafe", "azul-noche"],
                "gafete": ["blanco", "negro", "verde-claro", "beiches", "dorado", "cafe", "azul-noche"],
                "gorra": ["blanco", "negro", "verde-claro", "beiches", "dorado", "cafe", "azul-noche"],
                "pañoleta": ["blanco", "negro", "verde-claro", "beiches", "dorado", "cafe", "azul-noche"],
                "presillas": ["blanco", "negro", "verde-claro", "beiches", "dorado", "cafe", "azul-noche"],
                "rh": ["blanco", "negro", "verde-claro", "beiches", "dorado", "cafe", "azul-noche"]
            }
        };
        
        const identidad = (state.identidad || "").toLowerCase().trim();
        const producto = (state.producto || "").toLowerCase().trim();
        
        let coloresPermitidos = [];
        
        // Obtener colores permitidos
        if (colorMatriz[identidad] && colorMatriz[identidad][producto]) {
            coloresPermitidos = colorMatriz[identidad][producto];
        } else {
            // Si no hay configuración, mostrar todos
            document.querySelectorAll("[data-color]").forEach((btn) => {
                btn.style.display = "block";
                btn.style.opacity = "1";
                btn.style.cursor = 'pointer';
            });
            return;
        }
        
        // Aplicar filtrado
        document.querySelectorAll("[data-color]").forEach((btn) => {
            const color = btn.dataset.color;
            const permitido = coloresPermitidos.includes(color);

            if (permitido) {
                btn.style.display = "block";
                btn.style.opacity = "1";
                btn.style.cursor = 'pointer';
                btn.classList.remove("color-deshabilitado");
            } else {
                btn.style.display = "none";
                btn.classList.add("color-deshabilitado");
            }
            
            // SIEMPRE mostrar solo color sólido en los cuadritos
            const muestra = btn.querySelector(".muestra-color");
            if (muestra) {
                muestra.style.backgroundImage = "none";
                const colorHex = getColorHex(color);
                muestra.style.backgroundColor = colorHex || "#cccccc";
            }
        });
        
        // Si el color actual no es permitido, cambiar al primero permitido
        if (coloresPermitidos.length > 0 && !coloresPermitidos.includes(state.color)) {
            state.color = coloresPermitidos[0];
            const btn = document.querySelector(`[data-color="${coloresPermitidos[0]}"]`);
            if (btn) {
                setActiveClass(document.querySelectorAll("[data-color]"), el => el === btn, "seleccionada");
                updateSummary();
            }
        }
    }

    function validarPaso1Realtime() {
        const nombre = document.getElementById("input-nombre").value.trim();
        const rango = document.getElementById("input-rango").value.trim();
        const direccion = document.getElementById("input-direccion").value.trim();
        const correo = document.getElementById("input-correo").value.trim();
        const telefono = document.getElementById("input-telefono").value.trim();
        const btnSiguiente = document.getElementById("btn-siguiente-paso1");
        
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const emailValido = emailRegex.test(correo);
        
        const camposCompletos = nombre && rango && direccion && correo && telefono && emailValido && state.identidad && state.tecnica;
        
        if (btnSiguiente) {
            // btnSiguiente.disabled = !camposCompletos;
            btnSiguiente.style.opacity = camposCompletos ? "1" : "0.5";
            btnSiguiente.style.cursor = 'pointer';
        }
    }

    function validarPaso2Realtime() {
        const btnSiguiente = document.getElementById("btn-siguiente-paso2");
        const camposCompletos = state.producto;
        
        if (btnSiguiente) {
            // btnSiguiente.disabled = !camposCompletos;
            btnSiguiente.style.opacity = camposCompletos ? "1" : "0.5";
            btnSiguiente.style.cursor = 'pointer';
        }
    }

    function validarPaso3Realtime() {
        const btnSiguiente = document.getElementById("btn-siguiente-paso3");
        const camposCompletos = state.color;
        
        if (btnSiguiente) {
            // btnSiguiente.disabled = !camposCompletos;
            btnSiguiente.style.opacity = camposCompletos ? "1" : "0.5";
            btnSiguiente.style.cursor = 'pointer';
        }
    }

    function validarPaso4Realtime() {
        const btnSiguiente = document.getElementById("btn-siguiente-paso4");
        const camposCompletos = state.estampado;
        
        if (btnSiguiente) {
            // btnSiguiente.disabled = !camposCompletos;
            btnSiguiente.style.opacity = camposCompletos ? "1" : "0.5";
            btnSiguiente.style.cursor = 'pointer';
        }
    }

    function validarPaso5Realtime() {
        const btnFinalizar = document.getElementById("btn-finalizar-paso5");
        const camposCompletos = state.talla;
        
        if (btnFinalizar) {
            btnFinalizar.style.opacity = camposCompletos ? "1" : "0.5";
            btnFinalizar.style.cursor = 'pointer';
        }
    }

    function bindSelections() {
        if (btnVistaDelantera) {
            btnVistaDelantera.addEventListener("click", () => {
                state.vistaPrenda = "delantera";
                btnVistaDelantera.classList.add("active");
                btnVistaDelantera.style.backgroundColor = "#ffd700";
                btnVistaDelantera.style.color = "#000";
                btnVistaDelantera.style.fontWeight = "bold";
                btnVistaTrasera.classList.remove("active");
                btnVistaTrasera.style.backgroundColor = "#f0f0f0";
                btnVistaTrasera.style.color = "#333";
                btnVistaTrasera.style.fontWeight = "normal";
                updateSummary();
            });
        }

        if (btnVistaTrasera) {
            btnVistaTrasera.addEventListener("click", () => {
                state.vistaPrenda = "trasera";
                btnVistaTrasera.classList.add("active");
                btnVistaTrasera.style.backgroundColor = "#ffd700";
                btnVistaTrasera.style.color = "#000";
                btnVistaTrasera.style.fontWeight = "bold";
                btnVistaDelantera.classList.remove("active");
                btnVistaDelantera.style.backgroundColor = "#f0f0f0";
                btnVistaDelantera.style.color = "#333";
                btnVistaDelantera.style.fontWeight = "normal";
                updateSummary();
            });
        }

        // Validación en tiempo real para paso 1
        const inputNombre = document.getElementById("input-nombre");
        const inputRango = document.getElementById("input-rango");
        const inputDireccion = document.getElementById("input-direccion");
        const inputCorreo = document.getElementById("input-correo");
        const inputTelefono = document.getElementById("input-telefono");
        const btnSiguientePaso1 = document.getElementById("btn-siguiente-paso1");
        
        if (inputNombre) inputNombre.addEventListener("input", validarPaso1Realtime);
        if (inputRango) inputRango.addEventListener("input", validarPaso1Realtime);
        if (inputDireccion) inputDireccion.addEventListener("input", validarPaso1Realtime);
        if (inputCorreo) inputCorreo.addEventListener("input", validarPaso1Realtime);
        if (inputTelefono) inputTelefono.addEventListener("input", validarPaso1Realtime);
        
        // Desabilitar el botón inicialmente
        if (btnSiguientePaso1) {
            btnSiguientePaso1.style.opacity = "0.5";
            btnSiguientePaso1.style.cursor = 'pointer';
        }
        
        // Manejar captura de datos personales en paso 1
        if (btnSiguientePaso1) {
            btnSiguientePaso1.addEventListener("click", () => {
                state.nombre = document.getElementById("input-nombre").value;
                state.rango = document.getElementById("input-rango").value;
                state.direccion = document.getElementById("input-direccion").value;
                state.correo = document.getElementById("input-correo").value;
                state.telefono = document.getElementById("input-telefono").value;
                
                // Set default values if unchanged
                const opcionActiva = document.querySelector("[data-opcion].activo");
                if (!state.identidad && opcionActiva) state.identidad = opcionActiva.dataset.opcion;
                
                const tecnicaActiva = document.querySelector("[data-tecnica].activo");
                if (!state.tecnica && tecnicaActiva) state.tecnica = tecnicaActiva.dataset.tecnica;
                else if (!state.tecnica) state.tecnica = 'impresion';
                
                if (validarPaso(1)) {
                    changeStep(2);
                }
            });
        }

        // Manejar selección de identidad pública
        document.querySelectorAll("[data-opcion]").forEach((button) => {
            button.addEventListener("click", () => {
                state.identidad = button.dataset.opcion;
                setActiveClass(
                    document.querySelectorAll("[data-opcion]"),
                    (element) => element === button,
                    "activo"
                );
                updateColorAvailability();
                updateSummary();
                validarPaso1Realtime();
            });
        });

        document.querySelectorAll("[data-producto]").forEach((button) => {
            button.addEventListener("click", () => {
                let productoSeleccionado = button.dataset.producto;
                if (productoSeleccionado === "panoleta") productoSeleccionado = "pañoleta";
                state.producto = productoSeleccionado;
                setActiveClass(
                    document.querySelectorAll("[data-producto]"),
                    (element) => element === button,
                    "seleccionada"
                );
                updateTabsByProduct();
                updateTallaVisibility();
                updateColorAvailability();
                updateSummary();
                validarPaso2Realtime();
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
                validarPaso1Realtime();
            });
        });

        document.querySelectorAll("[data-color]").forEach((button) => {
            button.addEventListener("click", () => {
                // Permitir seleccionar solo si está visible (display no es none)
                if (window.getComputedStyle(button).display === "none") {
                    return;
                }
                
                state.color = button.dataset.color;
                setActiveClass(
                    document.querySelectorAll("[data-color]"),
                    (element) => element === button,
                    "seleccionada"
                );
                updateSummary();
                validarPaso3Realtime();
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
                validarPaso4Realtime();
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
                validarPaso5Realtime();
            });
        });

        // Botones de vista delantera/trasera (si también hubieran otros que usen la misma clase)
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

        // Botones de navegación Siguiente/Atrás
        document.getElementById("btn-siguiente-paso2")?.addEventListener("click", () => {
            if (validarPaso(2)) changeStep(3);
        });

        // Deshabilitar botón Atrás en paso 1 (es el primer paso)
        const btnAtrasPaso1 = document.getElementById("btn-atras-paso1");
        if (btnAtrasPaso1) {
            btnAtrasPaso1.disabled = true;
            btnAtrasPaso1.style.opacity = "0.5";
            btnAtrasPaso1.style.cursor = 'not-allowed';
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
                alert("✅ Personalización completada. Resumen:\n\nNombre: " + state.nombre + "\nRango: " + state.rango + "\nDirección: " + state.direccion + "\nCorreo: " + state.correo + "\nTeléfono: " + state.telefono + "\n\nIdentidad: " + formatLabel(state.identidad) + "\nTécnica: " + (state.tecnica === "bordado" ? "Bordado" : "Impresión") + "\nProducto: " + (productLabels[state.producto] || formatLabel(state.producto)) + "\nColor: " + formatLabel(state.color) + "\nEstampado: " + (state.estampado ? formatLabel(state.estampado) : "Ninguno") + "\nTalla: " + state.talla);
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
                const tecnica = state.tecnica === "bordado" ? "Bordado" : "Impresión";
                const color = formatLabel(state.color);
                const estampado = state.estampado ? formatLabel(state.estampado) : "Ninguno";
                const talla = state.talla || "Sin talla";
                
                alert(`✅ Producto agregado al carrito:\n\nNombre: ${state.nombre}\nRango: ${state.rango}\nDirección: ${state.direccion}\nCorreo: ${state.correo}\nTeléfono: ${state.telefono}\n\n${producto}\nIdentidad: ${identidad}\nTécnica: ${tecnica}\nColor: ${color}\nEstampado: ${estampado}\nTalla: ${talla}\nPrecio: ${priceMap[state.producto] || "$ 45.000"}`);
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
    updateEstampados();
    updateTallaVisibility();
    updateColorAvailability();
    updateStepIndicators();
    updateSummary();
    
    changeStep(state.pasoActual);
})();
