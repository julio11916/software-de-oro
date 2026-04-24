(function () {
    const state = {
        // Datos personales
        nombre: "",
        rango: "",
        direccion: "",
        correo: "",
        telefono: "",
        anoContingencia: "",
        // Configuraci�n de la prenda
        genero: "unisex",
        identidad: "",
        producto: "",
        tecnica: "",
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
        pa�oleta: "$ 28.000",
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
        pa�oleta: "Pa�oleta",
        "buso-manga-larga": "Buso manga larga",
        "buso_tactico": "Buso T�ctico",
        "buso tactico": "Buso T�ctico",
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
            camiseta: "??",
            buso: "??",
            gorra: "??",
            pa�oleta: "??",
            "buso-manga-larga": "??",
            "buso_tactico": "??",
            "buso tactico": "??",
            presillas: "??",
            rh: "??",
        };
        
        return iconMap[state.producto] || "??";
    }

    function getProductImage() {
        const productName = (state.producto || "").toLowerCase().trim();
        const isBack = state.vistaPrenda === "trasera";
        const identidad = (state.identidad || "").toLowerCase().trim();
        
        // BUSO
        if (productName === "buso") {
            if (identidad === "ejercito") {
                return isBack 
                    ? "/static/img/prendas/ejercito/buso/buso-detras.png"
                    : "/static/img/prendas/ejercito/buso/buso-frente.png";
            } else if (identidad === "gaula") {
                return isBack 
                    ? "/static/img/prendas/gaula/buso/espalda-gaula.png"
                    : "/static/img/prendas/gaula/buso/frente-gaula.png";
            } else if (identidad === "policia") {
                return isBack 
                    ? "/static/img/prendas/Policia/buso/detras-buso.png"
                    : "/static/img/prendas/Policia/buso/frente-buso.png";
            } else if (identidad === "armada") {
                return isBack 
                    ? "/static/img/prendas/armada/buso/detras-buso.png"
                    : "/static/img/prendas/armada/buso/frente-buso.png";
            }
        }

        // BUSO MANGA LARGA
        if (productName === "buso-manga-larga" || productName === "buso_manga_larga" || productName === "buso manga larga") {
            if (identidad === "ejercito") {
                return isBack 
                    ? "/static/img/prendas/ejercito/busos-manga-larga/buso_manga_larga_de_espalda-removebg-preview.png"
                    : "/static/img/prendas/ejercito/busos-manga-larga/buso_manga_larga_de_frente-removebg-preview.png";
            } else if (identidad === "gaula") {
                return isBack 
                    ? "/static/img/prendas/gaula/buso_manga_larga/detras_gaula.png"
                    : "/static/img/prendas/gaula/buso_manga_larga/manga_larga_gaula.png";
            } else if (identidad === "policia") {
                return isBack 
                    ? "/static/img/prendas/Policia/buso_manga_larga/detras_policia.png"
                    : "/static/img/prendas/Policia/buso_manga_larga/frente_poli.png";
            } else if (identidad === "armada") {
                return isBack 
                    ? "/static/img/prendas/armada/buso-manga-larga/buso_manga_larga_de_espalda-removebg-preview.png"
                    : "/static/img/prendas/armada/buso-manga-larga/buso_manga_larga_de_frente-removebg-preview.png";
            }
        }

        // BUSO T�CTICO
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
            } else if (identidad === "armada") {
                return isBack 
                    ? "/static/img/prendas/armada/buso-tactico/buso_manga_larga_de_espalda-removebg-preview.png"
                    : "/static/img/prendas/armada/buso-tactico/buso_manga_larga_de_frente-removebg-preview.png";
            }
        }
        
        // CAMISETA / GUERRERA
        if (productName === "camiseta" || productName === "guerrera") {
            if (identidad === "ejercito") {
                return isBack 
                    ? "/static/img/prendas/ejercito/guerreras/guerrera-detras.png"
                    : "/static/img/prendas/ejercito/guerreras/guerrera-frente.png";
            } else if (identidad === "gaula") {
                return isBack 
                    ? "/static/img/prendas/gaula/guerrera/guerrera-espalda.png"
                    : "/static/img/prendas/gaula/guerrera/guerrera-frente.png";
            } else if (identidad === "policia") {
                return isBack 
                    ? "/static/img/prendas/Policia/guerrera/guerrera-detras.png"
                    : "/static/img/prendas/Policia/guerrera/guerrera-frente.png";
            } else if (identidad === "armada") {
                return isBack 
                    ? "/static/img/prendas/armada/guerrera/detras-guerrera.png"
                    : "/static/img/prendas/armada/guerrera/guerrera-frente.png";
            }
        }
        
        // GORRA
        if (productName === "gorra") {
            if (identidad === "ejercito") {
                return isBack 
                    ? "/static/img/prendas/ejercito/gorras/gorra-detras.png"
                    : "/static/img/prendas/ejercito/gorras/gorra-frente.png";
            } else if (identidad === "gaula") {
                return isBack 
                    ? "/static/img/prendas/gaula/gorras/gorra-detras.png"
                    : "/static/img/prendas/gaula/gorras/gorra-frente.png";
            } else if (identidad === "policia") {
                return isBack 
                    ? "/static/img/prendas/Policia/gorras/gorra-detras.png"
                    : "/static/img/prendas/Policia/gorras/gorra-frente.png";
            } else if (identidad === "armada") {
                return isBack 
                    ? "/static/img/prendas/armada/gorra/espaldar-armada.png"
                    : "/static/img/prendas/armada/gorra/frente-armada.png";
            }
        }
        
        // PA�OLETA
        if (productName === "pa�oleta" || productName === "panoleta") {
            if (identidad === "ejercito") {
                return isBack 
                    ? "/static/img/prendas/ejercito/pa�oletas/detras.png"
                    : "/static/img/prendas/ejercito/pa�oletas/frente.png";
            } else if (identidad === "gaula") {
                return isBack 
                    ? "/static/img/prendas/gaula/Pa�oletas/detras.png"
                    : "/static/img/prendas/gaula/Pa�oletas/frente.png";
            } else if (identidad === "policia") {
                return isBack 
                    ? "/static/img/prendas/Policia/pa�oletas/detras.png"
                    : "/static/img/prendas/Policia/pa�oletas/frente.png";
            } else if (identidad === "armada") {
                return isBack 
                    ? "/static/img/prendas/armada/pa�oleta/detras.png"
                    : "/static/img/prendas/armada/pa�oleta/frente.png";
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
            } else if (identidad === "armada") {
                return isBack 
                    ? "/static/img/prendas/armada/Rh/detras.png"
                    : "/static/img/prendas/armada/Rh/frente.png";
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
                    ? "/static/img/prendas/ejercito/gafete del nombre o apellido/reves-gafete.png"
                    : "/static/img/prendas/ejercito/gafete del nombre o apellido/frente.png";
            } else if (identidad.includes("gaula")) {
                return isBack 
                    ? "/static/img/prendas/gaula/gafete del nombre o apellido/reves-gafete.png"
                    : "/static/img/prendas/gaula/gafete del nombre o apellido/verde.png";
            } else if (identidad.includes("policia")) {
                return isBack 
                    ? "/static/img/prendas/Policia/gafete del nombre o apellido/respalda-gafete.png"
                    : "/static/img/prendas/Policia/gafete del nombre o apellido/frente-gafete.png";
            }
        }
        return null;
    }

    // Funci�n para obtener la imagen de prenda con color espec�fico (para Paso 3)
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
            if (identidad === "ejercito") return `/static/img/prendas/ejercito/busos-manga-larga/buso_manga_larga_${colorName}.png`;
            if (identidad === "policia") return `/static/img/prendas/Policia/buso_manga_larga/buso${colorName === 'azul-noche' ? '-poli' : (colorName === 'verde' ? '_poli' : '-' + colorName)}.png`;
            if (identidad === "gaula") return `/static/img/prendas/gaula/buso_manga_larga/buso_manga_larga_${colorName}.png`;
        }

        // BUSO T�CTICO
        if (productName === "buso_tactico" || productName === "buso tactico" || productName === "buso-tactico") {
            if (identidad === "ejercito") return `/static/img/prendas/ejercito/buso_tactico/camisa_${colorName}.png`;
            if (identidad === "policia") return `/static/img/prendas/Policia/buso_tactico/tactico${colorName === 'azul-noche' ? '-poli' : ''}.png`;
            if (identidad === "gaula") return `/static/img/prendas/gaula/buso_tactico/${colorName}.png`;
        }

        // CAMISETA / GUERRERA
        if (productName === "camiseta" || productName === "guerrera") {
            if (identidad === "ejercito") return `/static/img/prendas/ejercito/guerreras/guerrera_ejercito.png`;
            if (identidad === "policia") {
                if (productName === "guerrera") return `/static/img/prendas/Policia/guerrera/guerrera_policia.png`;
                return isBack ? `/static/img/prendas/Policia/guerrera/guerrera-detras.png` : `/static/img/prendas/Policia/guerrera/guerrera-frente.png`;
            }
            if (identidad === "gaula") return `/static/img/prendas/gaula/guerrera/guerrera.png`;
        }

        // GORRA
        if (productName === "gorra") {
            if (color === "blanco") return null; // Sin blanco
            if (identidad === "ejercito") return `/static/img/prendas/ejercito/gorras/gorra_${colorName === 'negro' ? 'negra' : colorName}.png`;
            if (identidad === "policia") return `/static/img/prendas/Policia/gorras/gorra_${colorName === 'azul-noche' ? 'azul' : colorName}.png`;
            if (identidad === "gaula") return `/static/img/prendas/gaula/gorras/gorra_${colorName === 'negro' ? 'negra' : colorName}.png`;
        }

        // PA�OLETA
        if (productName === "pa�oleta" || productName === "panoleta") {
            if (identidad === "ejercito") return `/static/img/prendas/ejercito/pa�oletas/panoleta_${colorName}.png`;
            if (identidad === "policia") {
                if (colorName === 'azul-noche') return `/static/img/prendas/Policia/pa�oletas/pa�oleta-azul.png`;
                return `/static/img/prendas/Policia/pa�oletas/panoleta_${colorName}.png`;
            }
            if (identidad === "gaula") return `/static/img/prendas/gaula/Pa�oletas/panoleta_${colorName}.png`;
        }
        
        // RH
        if (productName === "rh") {
            if (identidad === "ejercito") {
                return colorName === 'cafe' ? `/static/img/prendas/ejercito/Rh/rh_cafe.png` : `/static/img/prendas/ejercito/Rh/rh.verde.png`;
            }
            if (identidad === "policia") {
                const bg = colorName === 'azul-noche' ? 'azul' : colorName;
                const sign = state.modeloRh || "O+"; // Si no han elegido RH, muestra O+ por defecto para ver el color
                
                // Mapeo detallado de archivos que s� existen en la carpeta de la Polic�a:
                const policiaRhMap = {
                    "A+azul": "A+,azul.png",
                    "A+verde": "A+-verde.png",
                    "A-azul": "A-azul.png",
                    "A-verde": "A-verde.rh.png",
                    "AB+azul": "AB+.azul.png",
                    "AB+verde": "AB+rh_verde.png",
                    "AB-azul": "AB-azul.png",
                    "AB-verde": "AB-verde-rh.png",
                    "B+verde": "B+rh verde.png",
                    "B+azul": "B+_azul.png",
                    "B-azul": "B-azul.png",
                    "B-verde": "B-verde rh.png",
                    "O+azul": "O+azul,rh.png",
                    "O+verde": "O+rh.verde.png",
                    "O-azul": "O-azul .png",
                    "O-verde": "O-verde,rh.png"
                };

                const key = sign + bg;
                if (policiaRhMap[key]) {
                    return `/static/img/prendas/Policia/Rh/${policiaRhMap[key]}`;
                }
                
                // Fallback si no coinciden exactamente
                return `/static/img/prendas/Policia/Rh/rh_${bg}.png`;
            }
            if (identidad === "gaula") return `/static/img/prendas/gaula/Rh/rh.png`; 
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
        // Mapeo de nombres de color a c�digos hexadecimales
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
        const tecnica = state.tecnica === "bordado" ? "Bordado" : "Impresion";
        const color = formatLabel(state.color);
        const estampado = state.estampado ? formatLabel(state.estampado) : "Pendiente";
        const talla = state.talla || "Pendiente";

        // Formatear mes/a�o
        let contingenciaFmt = state.anoContingencia ? state.anoContingencia : "Pendiente";
        
        // Crear descripci�n completa con TODOS los pasos
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
        
        // Actualizar identidad y t�cnica
        const identidadPreview = document.getElementById("preview-identidad");
        const tecnicaPreview = document.getElementById("preview-tecnica");
        if (identidadPreview) identidadPreview.textContent = identidad;
        if (tecnicaPreview) tecnicaPreview.textContent = tecnica;

        // Mostrar preview con imagen del producto o �cono
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
            // Aumentar un poco el tama�o si es un accesorio peque�o como Gafetes, RH o Presillas
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
                // Fallback si la imagen de color espec�fico no existe
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
                    // Colocar el tipo de sangre en el div, ej: "A+", "O-", o "POS" si es lo que eligi�
                    let txtSangre = state.modeloRh || "";
                    if (txtSangre.includes("+")) txtSangre = txtSangre.replace("+", " POS");
                    if (txtSangre.includes("-")) txtSangre = txtSangre.replace("-", " NEG");
                    
                    if (state.identidad === "policia" && (state.color === "azul-noche" || state.color === "negro")) {
                    rhOverlayEl.style.color = "#ccff00"; // Ne�n para polic�as oscuros
                    rhOverlayEl.style.textShadow = "-1px -1px 0 #0d1b2a, 1px -1px 0 #0d1b2a, -1px 1px 0 #0d1b2a, 1px 1px 0 #0d1b2a";
                } else if (state.identidad === "policia" && state.color === "verde-claro") {
                    rhOverlayEl.style.color = "#d0d6c0"; // Hueso
                    rhOverlayEl.style.textShadow = "-1px -1px 0 #394524, 1px -1px 0 #394524, -1px 1px 0 #394524, 1px 1px 0 #394524";
                } else {
                    rhOverlayEl.style.color = "#000000"; // Negro s�lido est�ndar para otras fuerzas
                    rhOverlayEl.style.textShadow = "none";
                }

                rhOverlayEl.textContent = txtSangre;
            }
        }
        else if (isGafete && state.vistaPrenda !== "trasera") {
                overlayEl.style.display = "flex";
                
                // Determinar colores basados en la selecci�n o en la imagen mostrada
                let textColor = "#000000"; // Negro por defecto para la mayor�a de fuerzas
                let shadowColor = "transparent"; // Sin sombra por defecto
                let marginTopRango = "-1px";
                let topPosition = "30%";
                
                if (state.identidad === "policia") {
                    // La Polic�a usa texto con estilo "ne�n"
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
                } else if (state.identidad === "ejercito" || state.identidad === "gaula" || state.identidad === "armada") {
                    // Ej�rcito, Gaula y Armada usan texto negro s�lido, sin sombra
                    textColor = "#000000";
                    shadowColor = "transparent";
                    // Para Ej�rcito y Gaula usualmente el texto va centrado diferente
                    topPosition = "45%";
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
                
                // En el ej�rcito/Gaula a veces la placa tiene fondo de tela que dificulta la lectura
                // Si gustan del fondo se puede usar background-color: rgba(255,255,255,0.7)
                // Pero lo dejaremos transparente si no piden fondo blanco.
                divRango.style.background = "transparent";
                divNombre.style.background = "transparent";
                
                const rangoFinal = state.rango ? state.rango.charAt(0).toUpperCase() + state.rango.slice(1).toLowerCase() : 'Rango';
                const nombreFinal = state.nombre ? state.nombre.toUpperCase() : 'NOMBRE';
                
                divRango.textContent = rangoFinal;
                divNombre.textContent = nombreFinal;
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

    function validarPaso(paso) {
        switch(paso) {
            case 1:
                return validarPaso1Realtime(true);
            case 2:
                if (!state.producto) {
                    alert("?? Por favor selecciona un Producto");
                    return false;
                }
                break;
            case 3:
                if (!state.color) {
                    alert("?? Por favor selecciona un Color");
                    return false;
                }
                if (state.producto === "rh" && !state.modeloRh) {
                    alert("?? Por favor selecciona un Tipo de RH");
                    return false;
                }
                break;
            case 4:
                if (!state.estampado) {
                    alert("?? Por favor selecciona un Estampado");
                    return false;
                }
                break;
        }
        return true;
    }

    function changeStep(step) {
        console.log(`?? changeStep(${step}) - pasoActual: ${state.pasoActual} ? ${step}`);

        // Update the button text for dynamic steps
        const btnPasos3 = document.getElementById("btn-siguiente-paso3");
        const btnPasos4 = document.getElementById("btn-siguiente-paso4");
        
        if (state.producto) {
            const productoActual = state.producto.toLowerCase();
            
            // L�gica para el bot�n del paso 3
            if (btnPasos3) {
                const prendasTerminanPaso3 = ["rh", "gafete del nombre o apellido", "gafete", "presillas"];
                if (prendasTerminanPaso3.includes(productoActual)) {
                    btnPasos3.textContent = "? Finalizar";
                } else {
                    btnPasos3.textContent = "Siguiente ?";
                }
            }
            
            // L�gica para el bot�n del paso 4
            if (btnPasos4) {
                const prendasTerminanPaso4 = ["pa�oleta", "gorra"];
                if (prendasTerminanPaso4.includes(productoActual)) {
                    btnPasos4.textContent = "? Finalizar";
                } else {
                    btnPasos4.textContent = "Siguiente ?";
                }
            }
        }
        state.pasoActual = step;
        
        // ?? Actualizar Layout PRIMERO (para evitar que cualquier error detenga esto)
        updatePanelLayout();
        
        document.querySelectorAll(".paso-contenido").forEach((section) => {
            section.classList.toggle("seccion-hidden", section.id !== `paso${step}`);
            
            // Move info-producto dynamically to the left panel active step before its navigation buttons
            if (section.id === `paso${step}`) {
                const infoProducto = document.querySelector('.info-producto');
                const botonesNav = section.querySelector('.botones-navegacion');
                
                if (infoProducto) {
                    if (step > 1 && botonesNav) {
                        section.insertBefore(infoProducto, botonesNav);
                        infoProducto.style.display = 'block';
                    } else if (step === 1) {
                        // En el paso 1 no mostramos la info en el lado izquierdo
                        document.querySelector('.panel-derecho').appendChild(infoProducto);
                        infoProducto.style.display = 'none'; // o block si el panel derecho est� oculto de todos modos
                    }
                }
            }
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
                    console.log("  ? Estamos en paso 3 (COLOR), llamando updateColorAvailability()");
                    updateColorAvailability();
                    validarPaso3Realtime();
                    break;
                case 4:
                    validarPaso4Realtime();
                    break;
            }
        } catch(error) {
            console.error("Error en validaci�n de paso:", error);
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
        const prendasEspeciales = ["presillas", "rh", "pa�oleta", "gorra", "contingencia", "gafete del nombre o apellido"];
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

        // Establecer la pesta�a activa por defecto seg�n el producto
        tabs.forEach((tab) => {
            tab.classList.remove("activa");
            if (tab.dataset.area === defaultActiveArea && tab.style.display !== "none") {
                tab.classList.add("activa");
            }
        });

        // Habilitar todas las t�cnicas para todos los productos
        const tecnicaButtons = document.querySelectorAll("[data-tecnica]");
        tecnicaButtons.forEach((button) => {
            button.disabled = false;
            button.style.opacity = "1";
            button.style.cursor = "pointer";
        });
    }

    function updateTallaVisibility() {
        const btnSiguiente = document.getElementById("btn-siguiente-paso4");
        // En este caso, el paso 4 es el �ltimo y va hacia la confirmaci�n.
        if (btnSiguiente) btnSiguiente.style.display = "inline-block";
    }

    function updateEstampados() {
        const identidad = state.identidad ? state.identidad.toLowerCase().trim() : "policia";
        
        // Mapeo din�mico para todos los estampados
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
                    
                    // Solo actualizamos a la imagen si no da fallback vac�o o fallback manual de ser necesario.
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
        // Asegurarnos de mostrar el selector de variaciones (como el Tipo de Sangre)
        actualizarVarContainer(state.color, state.producto);

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
                "pa�oleta": ["verde-claro", "negro", "beiches"],
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
                "pa�oleta": ["verde-claro", "negro", "azul-noche"],
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
                "pa�oleta": ["blanco", "negro", "verde-claro", "beiches", "dorado", "cafe", "azul-noche"],
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
            // Todos permitidos
            coloresPermitidos = Array.from(document.querySelectorAll("[data-color]")).map(b => b.dataset.color);
        }
        
        const esRhSinModelo = producto === "rh" && !state.modeloRh;

        // Aplicar filtrado
        document.querySelectorAll("[data-color]").forEach((btn) => {
            const color = btn.dataset.color;
            const permitido = coloresPermitidos.includes(color);

            if (permitido) {
                btn.style.display = "block";
                
                if (esRhSinModelo) {
                    btn.classList.add("color-deshabilitado");
                    btn.classList.remove("seleccionada");
                    btn.style.opacity = "0.4";
                    btn.style.cursor = 'not-allowed';
                } else {
                    btn.style.opacity = "1";
                    btn.style.cursor = 'pointer';
                    btn.classList.remove("color-deshabilitado");
                }
            } else {
                btn.style.display = "none";
                btn.classList.add("color-deshabilitado");
            }
            
            // Mostrar imagen de la prenda si est� disponible, sino color s�lido
            const muestra = btn.querySelector(".muestra-color");
            if (muestra) {
                // Siempre mostrar color s�lido sin imagen para las opciones de color
                muestra.style.backgroundImage = "none";
                const colorHex = getColorHex(color);
                muestra.style.backgroundColor = colorHex || "#cccccc";
                muestra.style.border = "1px solid #999";
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

    function actualizarVarContainer(color, producto) {
        const container = document.getElementById("variaciones-color-container");
        if (!container) return;

        const product = producto ? producto.toLowerCase() : "";
        let htmlVariaciones = "";

        // Mostrar seleccion de RH general para todas las fuerzas
        if (product === "rh") {
            htmlVariaciones = `
                <label class="label-opcion" style="display: block; margin-top: 1rem; margin-bottom: 0.5rem; color: #333;">Tipo de Sangre (RH) <span class="text-danger">*</span></label>
                <select id="select-modelo-rh" class="form-control" style="max-width: 300px; margin-bottom: 1rem;">
                    <option value="" disabled selected>Seleccione su tipo de sangre</option>
                    <option value="O+">O+</option>
                    <option value="O-">O-</option>
                    <option value="A+">A+</option>
                    <option value="A-">A-</option>
                    <option value="B+">B+</option>
                    <option value="B-">B-</option>
                    <option value="AB+">AB+</option>
                    <option value="AB-">AB-</option>
                </select>
            `;
        }

        if (htmlVariaciones) {
            container.style.display = "block";
            if (!container.querySelector("#select-modelo-rh")) {
                container.innerHTML = htmlVariaciones;
            }
            
            const selectRh = document.getElementById("select-modelo-rh");
            if (selectRh) {
                // pre-select if state has it
                if (state.modeloRh) {
                    const optionExists = Array.from(selectRh.options).some(opt => opt.value === state.modeloRh);
                    if (optionExists) {
                        selectRh.value = state.modeloRh;
                    } else {
                        state.modeloRh = null;
                        state.color = null; // Reiniciamos color para forzar el flujo "Sangre -> Color"
                    }
                }

                selectRh.onchange = (e) => {
                    state.modeloRh = e.target.value;
                    // Llama de vuelta para habilitar los colores tras seleccionar RH
                    updateColorAvailability();
                    updateSummary();
                    validarPaso3Realtime();
                };
            }
        } else {
            container.style.display = "none";
            container.innerHTML = "";
            state.modeloRh = null;
        }
    }

    function validarPaso1Realtime(mostrarAlerta = false) {
        const inputNombre = document.getElementById("input-nombre");
        const inputRango = document.getElementById("input-rango");
        const inputDireccion = document.getElementById("input-direccion");
        const inputCorreo = document.getElementById("input-correo");
        const inputTelefono = document.getElementById("input-telefono");
        const inputAnoContingencia = document.getElementById("input-ano-contingencia");
        const inputMesContingencia = document.getElementById("input-mes-contingencia");
        const inputTalla = document.getElementById("input-talla");
        const btnSiguiente = document.getElementById("btn-siguiente-paso1");
        
        let valid = true;
        let mensajeAlerta = "";

        // Validar nombre: solo letras y espacios
        const nombreValido = inputNombre && /^[A-Za-z������������\s]+$/.test(inputNombre.value.trim());
        if (!nombreValido) { valid = false; mensajeAlerta += "- Nombre y Apellido (solo letras).\n"; }

        // Validar rango: solo letras y espacios
        const rangoValido = inputRango && /^[A-Za-z������������\s]+$/.test(inputRango.value.trim());
        if (!rangoValido) { valid = false; mensajeAlerta += "- Rango (solo letras).\n"; }

        // Validar direcci�n: cualquier caracter (solo q no est� vac�o)
        const dirValida = inputDireccion && inputDireccion.value.trim().length > 0;
        if (!dirValida) { valid = false; mensajeAlerta += "- Direcci�n.\n"; }

        // Validar correo
        const correoValido = inputCorreo && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(inputCorreo.value.trim());
        if (!correoValido) { valid = false; mensajeAlerta += "- Correo Electr�nico v�lido.\n"; }

        // Validar tel�fono: solo n�meros
        const telValido = inputTelefono && /^[0-9]+$/.test(inputTelefono.value.trim());
        if (!telValido) { valid = false; mensajeAlerta += "- Tel�fono (solo n�meros).\n"; }

        // Validar Mes y A�o de Contingencia
        const mesValido = inputMesContingencia && inputMesContingencia.value.trim().length > 0;
        const anoValido = inputAnoContingencia && inputAnoContingencia.value.trim().length > 0;
        if (!mesValido || !anoValido) { valid = false; mensajeAlerta += "- Mes y A�o de contingencia.\n"; }

        // Validar Entidad (Identidad) seleccionada
        if (!state.identidad) { valid = false; mensajeAlerta += "- Seleccionar una Entidad (Ej: Polic�a, Ej�rcito).\n"; }

        // Validar T�cnica seleccionada
        if (!state.tecnica) { valid = false; mensajeAlerta += "- Seleccionar una T�cnica (Ej: Bordado).\n"; }

        // Validar Talla
        const tallaValida = inputTalla && inputTalla.value.trim().length > 0;
        if (!tallaValida && !state.talla) { valid = false; mensajeAlerta += "- Seleccionar una Talla.\n"; }

        if (btnSiguiente) {
            btnSiguiente.style.opacity = valid ? "1" : "0.5";
            btnSiguiente.style.cursor = valid ? 'pointer' : 'not-allowed';
        }
        
        if (mostrarAlerta === true && !valid) {
            alert("Por favor, completa correctamente los siguientes campos obligatorios:\n\n" + mensajeAlerta);
        }

        return valid;
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
        
        let camposCompletos = false;
        
        if (state.producto === "rh") {
            camposCompletos = state.color && state.modeloRh;
        } else {
            camposCompletos = state.color;
        }
        
        if (btnSiguiente) {
            btnSiguiente.style.opacity = camposCompletos ? "1" : "0.5";
            btnSiguiente.style.cursor = camposCompletos ? 'pointer' : 'not-allowed';
        }
    }

    function validarPaso4Realtime() {
        const btnSiguiente = document.getElementById("btn-siguiente-paso4");
        const camposCompletos = state.estampado;
        
        if (btnSiguiente) {
            btnSiguiente.style.opacity = camposCompletos ? "1" : "0.5";
            btnSiguiente.style.cursor = 'pointer';
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

        // Validaci�n en tiempo real para paso 1
        const inputNombre = document.getElementById("input-nombre");
        const inputRango = document.getElementById("input-rango");
        const inputDireccion = document.getElementById("input-direccion");
        const inputCorreo = document.getElementById("input-correo");
        const inputTelefono = document.getElementById("input-telefono");
        const inputMesContingencia = document.getElementById("input-mes-contingencia");
        const inputAnoContingencia = document.getElementById("input-ano-contingencia");
        const inputTalla = document.getElementById("input-talla");
        const btnSiguientePaso1 = document.getElementById("btn-siguiente-paso1");
        
        if (inputNombre) inputNombre.addEventListener("input", validarPaso1Realtime);
        if (inputRango) inputRango.addEventListener("input", validarPaso1Realtime);
        if (inputDireccion) inputDireccion.addEventListener("input", validarPaso1Realtime);
        if (inputCorreo) inputCorreo.addEventListener("input", validarPaso1Realtime);
        if (inputTelefono) inputTelefono.addEventListener("input", validarPaso1Realtime);
        if (inputMesContingencia) {
            inputMesContingencia.addEventListener("change", () => {
                const mesVal = inputMesContingencia.value || "";
                const anoVal = inputAnoContingencia?.value || "";
                state.anoContingencia = mesVal && anoVal ? `${mesVal} ${anoVal}` : "";
                validarPaso1Realtime();
                updateSummary();
            });
        }
        if (inputAnoContingencia) {
            inputAnoContingencia.addEventListener("input", () => {
                const mesVal = inputMesContingencia?.value || "";
                const anoVal = inputAnoContingencia.value || "";
                state.anoContingencia = mesVal && anoVal ? `${mesVal} ${anoVal}` : "";
                validarPaso1Realtime();
                updateSummary();
            });
        }
        if (inputTalla) {
            inputTalla.addEventListener("change", () => {
                state.talla = inputTalla.value;
                updateSummary();
                validarPaso1Realtime();
            });
        }
        
        // Desabilitar el bot�n inicialmente
        if (btnSiguientePaso1) {
            btnSiguientePaso1.style.opacity = "0.5";
            btnSiguientePaso1.style.cursor = 'pointer';
        }
        
        // Manejar captura de datos personales en paso 1
        if (btnSiguientePaso1) {
            btnSiguientePaso1.addEventListener("click", () => {
                if (!validarPaso1Realtime(true)) {
                    return; // Detener si falta alg�n campo o es inv�lido
                }
                state.nombre = document.getElementById("input-nombre").value;
                state.rango = document.getElementById("input-rango").value;
                state.direccion = document.getElementById("input-direccion").value;
                state.correo = document.getElementById("input-correo").value;
                state.telefono = document.getElementById("input-telefono").value;
                const mesVal = document.getElementById("input-mes-contingencia")?.value || "";
                const anoVal = document.getElementById("input-ano-contingencia")?.value || "";
                state.anoContingencia = mesVal && anoVal ? `${mesVal} ${anoVal}` : "";
                
                // Set default values if unchanged
                const opcionActiva = document.querySelector("[data-opcion].activo");
                if (!state.identidad && opcionActiva) state.identidad = opcionActiva.dataset.opcion;
                
                const tecnicaActiva = document.querySelector("[data-tecnica].activo");
                if (!state.tecnica && tecnicaActiva) state.tecnica = tecnicaActiva.dataset.tecnica;
                
                const inputTalla = document.getElementById("input-talla");
                if (!state.talla && inputTalla && inputTalla.value) state.talla = inputTalla.value;
                
                // Forzar la validaci�n aqu�
                if (!state.identidad || !state.tecnica || !state.talla) {
                    alert("Aseg�rate de seleccionar una Entidad, T�cnica y Talla.");
                    return;
                }
                
                if (validarPaso(1)) {
                    changeStep(2);
                }
            });
        }

        // Manejar selecci�n de identidad p�blica
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
                // Permitir seleccionar solo si est� visible (display no es none)
                if (window.getComputedStyle(button).display === "none") {
                    return;
                }
                
                if (button.classList.contains("color-deshabilitado")) {
                    if (state.producto === "rh" && !state.modeloRh) {
                        alert("?? Por favor selecciona primero tu Tipo de Sangre.");
                    }
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
                
                // Aplicar color al dise�o 3D
                if (window.aplicarColorPrenda) {
                    window.aplicarColorPrenda(state.color);
                }

                // Mostrar desplegable de variaciones (si aplica)
                actualizarVarContainer(state.color, state.producto);
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
                validarPaso1Realtime();
            });
        });

        // Botones de vista delantera/trasera (si tambi�n hubieran otros que usen la misma clase)
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

        // Botones de navegaci�n Siguiente/Atr�s
        document.getElementById("btn-siguiente-paso2")?.addEventListener("click", () => {
            if (validarPaso(2)) {
                // Verificar si hay prendas que acaban en paso 2 directamente. (no especificado, va a 3 default)
                changeStep(3);
            } else {
                alert("Por favor selecciona un producto.");
            }
        });

        // Deshabilitar bot�n Atr�s en paso 1 (es el primer paso)
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
            if (validarPaso(3)) {
                if(state.producto === "rh" && (!state.color || !state.modeloRh)) {
                    alert("Por favor selecciona un color y el tipo de RH.");
                    return;
                } else if (!state.color) {
                    alert("Por favor selecciona un color.");
                    return;
                }
                
                // Verificar a qu� paso ir: las prendas como RH, Gafetes, Presillas finalizan AQU� (paso 3)
                const prendasTerminanPaso3 = ["rh", "gafete del nombre o apellido", "gafete", "presillas"];
                const productoActual = state.producto.toLowerCase();

                if (prendasTerminanPaso3.includes(productoActual)) {
                    finalizarOrden();
                } else {
                    changeStep(4);
                }
            } else {
                alert("Por favor selecciona un color.");
            }
        });

        document.getElementById("btn-atras-paso3")?.addEventListener("click", () => {
            changeStep(2);
        });

        document.getElementById("btn-siguiente-paso4")?.addEventListener("click", () => {
            if (validarPaso(4)) {
                finalizarOrden();
            } else {
                alert("Por favor selecciona un estampado.");
            }
        });

        document.getElementById("btn-atras-paso4")?.addEventListener("click", () => {
            changeStep(3);
        });

        function finalizarOrden() {
            updateSummary();
            alert("? Personalizaci�n completada. Resumen:\n\nNombre: " + state.nombre + "\nRango: " + state.rango + "\nDirecci�n: " + state.direccion + "\nCorreo: " + state.correo + "\nTel�fono: " + state.telefono + "\nA�o contingencia: " + state.anoContingencia + "\n\nIdentidad: " + formatLabel(state.identidad) + "\nT�cnica: " + (state.tecnica === "bordado" ? "Bordado" : "Impresion") + "\nProducto: " + (productLabels[state.producto] || formatLabel(state.producto)) + "\nColor: " + formatLabel(state.color) + "\nEstampado: " + (state.estampado ? formatLabel(state.estampado) : "Ninguno") + "\nTalla: " + (state.talla || "No aplica"));
        }

        // Bot�n Atr�s en el panel derecho
        document.getElementById("btn-atras-panel")?.addEventListener("click", () => {
            if (state.pasoActual > 1) {
                changeStep(state.pasoActual - 1);
            } else {
                alert("?? Ya est�s en el primer paso");
            }
        });

        // Bot�n Agregar al Carrito
        document.getElementById("btn-agregar-carrito")?.addEventListener("click", () => {
            if (validarPaso(4)) {
                const producto = productLabels[state.producto] || formatLabel(state.producto);
                const identidad = formatLabel(state.identidad);
                const tecnica = state.tecnica === "bordado" ? "Bordado" : "Impresion";
                const color = formatLabel(state.color);
                const estampado = state.estampado ? formatLabel(state.estampado) : "Ninguno";
                const talla = state.talla || "Sin talla";
                
                alert(`? Producto agregado al carrito:\n\nNombre: ${state.nombre}\nRango: ${state.rango}\nDirecci�n: ${state.direccion}\nCorreo: ${state.correo}\nTel�fono: ${state.telefono}\nA�o contingencia: ${state.anoContingencia}\n\n${producto}\nIdentidad: ${identidad}\nT�cnica: ${tecnica}\nColor: ${color}\nEstampado: ${estampado}\nTalla: ${talla}\nPrecio: ${priceMap[state.producto] || "$ 45.000"}`);
            } else {
                alert("?? Por favor completa todos los campos antes de agregar al carrito");
            }
        });

        // Deshabilitar navegaci�n por pasos si no se han completado los requeridos
        for (let i = 1; i <= 4; i++) {
            const stepHeader = document.getElementById(`paso${i}-header`);
            if (stepHeader) {
                // Remove pointer cursor since we are disabling jumping around
                stepHeader.style.cursor = "default";
                /* // Comentado para evitar avanzar si no se cumplen requisitos
                stepHeader.addEventListener("click", () => {
                    changeStep(i);
                });
                */
                // Hacer el contenedor del paso tambi�n no clickeable
                const stepContainer = stepHeader.parentElement;
                if (stepContainer) {
                    stepContainer.style.cursor = "default";
                    /*
                    stepContainer.addEventListener("click", () => {
                        changeStep(i);
                    });
                    */
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






