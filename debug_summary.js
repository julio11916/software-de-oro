    function updateSummary() {
        const producto = productLabels[state.producto] || formatLabel(state.producto);
        const identidad = formatLabel(state.identidad);
        const tecnica = state.tecnica === "bordado" ? "Bordado" : "Impresion";
        const color = formatLabel(state.color);
        const estampado = state.estampado ? formatLabel(state.estampado) : "Pendiente";
        const talla = state.talla || "Pendiente";

        // Formatear mes/año
        let contingenciaFmt = state.anoContingencia ? state.anoContingencia : "Pendiente";
        
        // Crear descripción completa con TODOS los pasos
        let modeloTxt = "";
        if (state.producto === "rh" && state.modeloRh) {
            modeloTxt = ` | Tipo de Sangre: ${state.modeloRh}`;
        }
        
        const isEspecial = ["rh", "presillas", "gafete", "gafete del nombre o apellido"].includes((state.producto || "").toLowerCase());
        
        let descripcionCompleta = `${identidad} | ${tecnica} | ${contingenciaFmt} | ${producto}${modeloTxt} | Color: ${color}`;
        
        if (!isEspecial) {
            descripcionCompleta += ` | Talla: ${talla} | Estampado: ${estampado}`;
        }

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
        
        if (estampadoInfoPreview) {
            estampadoInfoPreview.textContent = isEspecial ? "No aplica" : estampado;
            // Ocultar el elemento padre si es especial
            const filaEstampado = estampadoInfoPreview.parentElement;
            if (filaEstampado && filaEstampado.classList.contains('info-item')) {
                filaEstampado.style.display = isEspecial ? 'none' : '';
            }
        }
        
        if (tallaInfoPreview) {
            tallaInfoPreview.textContent = isEspecial ? "No aplica" : talla;
            const filaTalla = tallaInfoPreview.parentElement;
            if (filaTalla && filaTalla.classList.contains('info-item')) {
                filaTalla.style.display = isEspecial ? 'none' : '';
            }
        }
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
            if ((state.producto || "").toLowerCase() === "rh" && (!state.color || !state.modeloRh)) {
                imagen = getProductImage();
            } else if (state.color) {
                imagen = getProductColorImage(state.color);
            }
        }

        // Si no hay imagen de color o estamos antes del paso 3, usar la imagen base
        if (!imagen) {
            imagen = getProductImage();
        }

        if (imagen) {
            // Aumentar un poco el tamaño si es un accesorio pequeño como Gafetes, RH o Presillas
            let scaleStyle = "";
            const isGafete = state.producto === "gafete del nombre o apellido" || state.producto === "gafete";
            const isRh = state.producto === "rh";
            const isSmallItem = isRh || state.producto === "presillas";
            
            if (isGafete || isRh) {
                scaleStyle = "transform: scale(2.2);";
            } else if (isSmallItem) {
                scaleStyle = "transform: scale(1.6);";
            }

            let existingContainer = preview.querySelector("#preview-container");
            
            if (!existingContainer) {
                preview.innerHTML = `
                    <div id="preview-container" style="position: relative; text-align: center; background: white; width: 100%; height: 300px; display: flex; justify-content: center; align-items: center; overflow: hidden; border-radius: 8px;">
                        <img id="imagen-producto" src="" alt="Vista Previa" style="width: 100%; height: 100%; max-width: 260px; max-height: 260px; object-fit: contain; transition: transform 0.2s ease-in-out; z-index: 1;">
                        <div id="gafete-overlay" style="display: none; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%) scale(1.2); text-align: center; width: 60%; color: #000; font-family: 'Arial Rounded MT Bold', 'Helvetica Rounded', Arial, sans-serif; white-space: nowrap; z-index: 5; flex-direction: column; align-items: center; justify-content: center; letter-spacing: 0.5px; background: transparent; padding: 0;">
                            <div id="overlay-rango" style="font-size: 6px; font-weight: 800; margin-bottom: 2px;"></div>
                            <div id="overlay-nombre" style="font-size: 8px; font-weight: 900; text-transform: uppercase; letter-spacing: 0px;"></div>
                        </div>
                        <div id="rh-overlay" style="display: none; position: absolute; top: 45%; left: 50%; transform: translate(-50%, -50%) scale(2.5); text-align: center; color: #000; font-family: 'Arial Black', Arial, sans-serif; white-space: nowrap; z-index: 5; font-size: 18px; font-weight: 900; text-shadow: 1px 1px 2px rgba(255,255,255,0.4); background: transparent; padding: 0;">
                        </div>
                    </div>
                `;
            }
            
            let imgEl = preview.querySelector("#imagen-producto");
            imgEl.src = imagen;
            imgEl.alt = state.producto || 'Vista Previa de Prenda';
            imgEl.onerror = function() {
                // Fallback si la imagen de color específico no existe
                const fallbackImg = getProductImage();
                if (this.src !== window.location.origin + fallbackImg && fallbackImg) {
                    this.src = fallbackImg;
                } else {
                    this.style.display = 'none';
                }
            };
            imgEl.style.display = 'block';
            
            if (isGafete || isRh) { imgEl.style.transform = "scale(2.2)"; } else if (isSmallItem) { imgEl.style.transform = "scale(1.6)"; } else { imgEl.style.transform = "none"; }
            
            let overlayEl = preview.querySelector("#gafete-overlay");
            let rhOverlayEl = preview.querySelector("#rh-overlay");
            
            // Ocultar ambos por defecto
            if (overlayEl) overlayEl.style.display = "none";
            if (rhOverlayEl) rhOverlayEl.style.display = "none";

            if (isRh && state.vistaPrenda !== "trasera") {
                if (rhOverlayEl && state.modeloRh) {
                    rhOverlayEl.style.display = "block";
                    // Colocar el tipo de sangre en el div, ej: "A+", "O-", o "POS" si es lo que eligió
                    let txtSangre = state.modeloRh || "";
                    if (txtSangre.includes("+")) txtSangre = txtSangre.replace("+", " POS");
                    if (txtSangre.includes("-")) txtSangre = txtSangre.replace("-", " NEG");
                    
                    if (state.identidad === "policia" && (state.color === "azul-noche" || state.color === "negro")) {
                    rhOverlayEl.style.color = "#ccff00"; // Neón para policías oscuros
                    rhOverlayEl.style.textShadow = "-1px -1px 0 #0d1b2a, 1px -1px 0 #0d1b2a, -1px 1px 0 #0d1b2a, 1px 1px 0 #0d1b2a";
                } else if (state.identidad === "policia" && state.color === "verde-claro") {
                    rhOverlayEl.style.color = "#d0d6c0"; // Hueso
                    rhOverlayEl.style.textShadow = "-1px -1px 0 #394524, 1px -1px 0 #394524, -1px 1px 0 #394524, 1px 1px 0 #394524";
                } else {
                    rhOverlayEl.style.color = "#000000"; // Negro sólido estándar para otras fuerzas
                    rhOverlayEl.style.textShadow = "none";
                }

                rhOverlayEl.textContent = txtSangre;
            }
        }
        else if (isGafete && state.vistaPrenda !== "trasera") {
                overlayEl.style.display = "flex";
                
                // Determinar colores basados en la selección o en la imagen mostrada
                let textColor = "#000000"; // Negro por defecto para la mayoría de fuerzas
                let shadowColor = "transparent"; // Sin sombra por defecto
                let marginTopRango = "-1px";
                let topPosition = "30%";
                
                if (state.identidad === "policia") {
                    // La Policía usa texto con estilo "neón"
                    if ((imagen && imagen.includes("verde")) || state.color === "verde-claro") {
                        textColor = "#d0d6c0"; // Blanco hueso / verde muy claro
                        shadowColor = "#394524"; // Sombra verde oliva oscuro
                    } else if ((imagen && (imagen.includes("azul") || imagen.includes("negro"))) || state.color === "azul-noche" || state.color === "negro") {
                        textColor = "#ccff00"; // Neon green
                        shadowColor = "#0d1b2a"; // Sombra negra/azul oscuro
                    } else if (!state.color) {
                        if (imagen && imagen.includes("frente-gafete")) {
                            textColor = "#d0d6c0"; 
                            shadowColor = "#394524";
                        } else {
                            textColor = "#ccff00";
                            shadowColor = "#0d1b2a";
                        }
                    } else if (state.color === "blanco") {
                        textColor = "#000000"; 
                        shadowColor = "#ffffff";
                    }
                    topPosition = "44%";
                } else if (state.identidad === "ejercito" || state.identidad === "gaula" || state.identidad === "armada") {
                    // Ejército, Gaula y Armada usan texto negro sólido, sin sombra
                    if (state.identidad === "ejercito") {
                        textColor = "#1e2b14";
                        shadowColor = "rgba(0,0,0,0.8)";
                        topPosition = "45%";
                    } else {
                        textColor = "#000000";
                        shadowColor = "rgba(0, 0, 0, 0.6)";
                        topPosition = "52%";
                    }
                }

                overlayEl.style.top = topPosition;
                overlayEl.style.color = textColor;
                
                const shadowVal = shadowColor !== "transparent" 
                    ? `-1px -1px 0 ${shadowColor}, 1px -1px 0 ${shadowColor}, -1px 1px 0 ${shadowColor}, 1px 1px 0 ${shadowColor}` 
                    : 'none';
                
                // Aplicar estilos
                const divRango = preview.querySelector("#overlay-rango");
                const divNombre = preview.querySelector("#overlay-nombre");
                
                divRango.style.textShadow = shadowVal;
                divNombre.style.textShadow = shadowVal;

                if (state.identidad === "gaula" || state.identidad === "armada") {
                    divNombre.style.fontFamily = "'Arial Rounded MT Bold', 'Helvetica Rounded', Arial, sans-serif";
                    divRango.style.fontFamily = "'Arial Rounded MT Bold', 'Helvetica Rounded', Arial, sans-serif";
                    divNombre.style.order = "2";
                    divRango.style.order = "1";
                    divNombre.style.fontWeight = "900";
                    divRango.style.fontWeight = "800";
                    divNombre.style.transform = "none";
                    divRango.style.transform = "none";
                    divNombre.style.webkitTextStroke = "0.7px rgba(0,0,0,1)";
                    divRango.style.webkitTextStroke = "0.3px rgba(0,0,0,1)";
                } else {
                    divNombre.style.fontFamily = "'Arial Rounded MT Bold', 'Helvetica Rounded', Arial, sans-serif";
                    divRango.style.fontFamily = "'Arial Rounded MT Bold', 'Helvetica Rounded', Arial, sans-serif";
                    divNombre.style.order = "2";
                    divRango.style.order = "1";
                    divNombre.style.transform = "none";
                }
                
                // En el ejército/Gaula a veces la placa tiene fondo de tela que dificulta la lectura
                // Si gustan del fondo se puede usar background-color: rgba(255,255,255,0.7)
                // Pero lo dejaremos transparente si no piden fondo blanco.
                divRango.style.background = "transparent";
                divNombre.style.background = "transparent";
                
                const rangoFinal = state.rango ? state.rango.charAt(0).toUpperCase() + state.rango.slice(1).toLowerCase() : 'Rango';
                const nombreFinal = state.nombre ? state.nombre.toUpperCase() : 'NOMBRE';
                
                divRango.textContent = rangoFinal;
                divNombre.textContent = nombreFinal;
                
                // Escalar font sizes para armada, gaula y policia
                if (state.identidad !== "ejercito") {
                    divNombre.style.fontSize = "28px";
                    divRango.style.fontSize = "18px";
                }
            } else {
                overlayEl.style.display = "none";
            }
            if (!isRh || state.vistaPrenda === "trasera") {
                if (rhOverlayEl) rhOverlayEl.style.display = "none";
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

