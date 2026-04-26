(function () {
try {
    const state = {
        // Datos personales
        nombre: "",
        rango: "",
        direccion: "",
        correo: "",
        telefono: "",
        anoContingencia: "",
        // Configuracin de la prenda
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
        paoleta: "$ 28.000",
        panoleta: "$ 28.000",
        "pañoleta": "$ 28.000",
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
        paoleta: "Paoleta",
        panoleta: "Pañoleta",
        "pañoleta": "Pañoleta",
        "buso-manga-larga": "Buso manga larga",
        "buso_tactico": "Buso Tctico",
        "buso tactico": "Buso Tctico",
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
            paoleta: "??",
            panoleta: "??",
            "pañoleta": "??",
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
                    : "/static/img/prendas/gaula/buso_manga_larga/frente manga_larga_gaula.png";
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

        // BUSO TCTICO
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

        // PAÑOLETA
        if (productName.includes("pañoleta") || productName.includes("panoleta") || productName.includes("paoleta")) {
            if (identidad === "ejercito") {
                return isBack 
                    ? "/static/img/prendas/ejercito/pañoletas/detras.png"
                    : "/static/img/prendas/ejercito/pañoletas/frente.png";
            } else if (identidad === "gaula") {
                return isBack 
                    ? "/static/img/prendas/gaula/Pañoletas/detras.png"
                    : "/static/img/prendas/gaula/Pañoletas/frente.png";
            } else if (identidad === "policia") {
                return isBack 
                    ? "/static/img/prendas/Policia/pañoletas/detras.png"
                    : "/static/img/prendas/Policia/pañoletas/frente.png";
            } else if (identidad === "armada") {
                return isBack
                    ? "/static/img/prendas/armada/pañoleta/detras.png"
                    : "/static/img/prendas/armada/pañoleta/frente.png";
            }
        }
        
        // RH
        if (productName === "rh") {
            if (identidad === "ejercito") {
                return isBack 
                    ? "/static/img/prendas/ejercito/Rh/espaldar.png"
                    : "/static/img/prendas/ejercito/Rh/frende.png";
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
        if (productName === "presillas" || productName === "presilla") {
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
                    : "/static/img/prendas/gaula/gafete del nombre o apellido/frente copy.png";
            } else if (identidad.includes("policia")) {
                return isBack 
                    ? "/static/img/prendas/Policia/gafete del nombre o apellido/respalda-gafete.png"
                    : "/static/img/prendas/Policia/gafete del nombre o apellido/frente-gafete.png";
            } else if (identidad.includes("armada")) {
                return isBack 
                    ? "/static/img/prendas/armada/gafete del nombre o apellido/espaldar.png"
                    : "/static/img/prendas/armada/gafete del nombre o apellido/frente.png";
            }
        }
        return null;
    }

    // Funcin para obtener la imagen de prenda con color especfico (para Paso 3)
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
            if (identidad === "armada") return `/static/img/prendas/armada/buso/buso_${colorName.replace("-claro","")}.png`;
        }

        // BUSO MANGA LARGA
        if (productName === "buso-manga-larga" || productName === "buso_manga_larga" || productName === "buso manga larga") {
            let clr = colorName.replace('-claro', '');
            if (identidad === "ejercito") return `/static/img/prendas/ejercito/busos-manga-larga/buso_manga_larga_${clr}.png`;
            if (identidad === "policia") return `/static/img/prendas/Policia/buso_manga_larga/buso${colorName === 'azul-noche' ? '-poli' : (colorName === 'verde' ? '_poli' : '-' + colorName)}.png`;
            if (identidad === "gaula") return `/static/img/prendas/gaula/buso_manga_larga/buso_manga_larga_${clr}.png`;
            if (identidad === "armada") return `/static/img/prendas/armada/buso-manga-larga/buso_manga_larga_${clr}.png`;
        }

        // BUSO TCTICO
        if (productName === "buso_tactico" || productName === "buso tactico" || productName === "buso-tactico") {
            if (identidad === "ejercito") return `/static/img/prendas/ejercito/buso_tactico/camisa_${colorName}.png`;
            if (identidad === "policia") return `/static/img/prendas/Policia/buso_tactico/tactico${colorName === 'azul-noche' ? '-poli' : ''}.png`;
            if (identidad === "gaula") return `/static/img/prendas/gaula/buso_tactico/${colorName}.png`;
            if (identidad === "armada") return isBack ? `/static/img/prendas/armada/buso-tactico/buso_manga_larga_de_espalda-removebg-preview.png` : `/static/img/prendas/armada/buso-tactico/buso tactico ${colorName.replace("-claro", "")}.png`;
        }

        // CAMISETA / GUERRERA
        if (productName === "camiseta" || productName === "guerrera") {
            if (identidad === "ejercito") return isBack ? `/static/img/prendas/ejercito/guerreras/guerrera-detras.png` : `/static/img/prendas/ejercito/guerreras/${colorName}.png`;
            if (identidad === "policia") {
                if (colorName === 'azul-noche') return `/static/img/prendas/Policia/guerrera/guerrera_policia.png`;
                if (colorName === 'verde') return `/static/img/prendas/Policia/guerrera/guerrera_poli.png`;
                return `/static/img/prendas/Policia/guerrera/guerrera_${colorName}.png`;
            }
            if (identidad === "gaula") return isBack ? `/static/img/prendas/gaula/guerrera/guerrera-espalda.png` : `/static/img/prendas/gaula/guerrera/guerrera%20${colorName}.png`;
            if (identidad === "armada") return isBack ? `/static/img/prendas/armada/guerrera/detras-guerrera.png` : `/static/img/prendas/armada/guerrera/guerrera ${colorName.replace("-claro", "")}.png`;
        }

        // GORRA
        if (productName === "gorra") {
            if (color === "blanco") return null; // Sin blanco
            if (identidad === "ejercito") return isBack ? `/static/img/prendas/ejercito/gorras/gorra-detras.png` : `/static/img/prendas/ejercito/gorras/verde.png`;
            if (identidad === "policia") {
                if (colorName === 'negro') return `/static/img/prendas/Policia/gorras/gorra_azul.png`; // Fallback si no existe negra per se
                return isBack ? `/static/img/prendas/Policia/gorras/gorra-detras.png` : `/static/img/prendas/Policia/gorras/gorra_${colorName === 'azul-noche' ? 'azul' : colorName}.png`;
            }
            if (identidad === "gaula") return `/static/img/prendas/gaula/gorras/gorra_${colorName === 'negro' ? 'negra' : colorName}.png`;
            if (identidad === "armada") return isBack ? `/static/img/prendas/armada/gorra/espaldar-armada.png` : `/static/img/prendas/armada/gorra/gorra ${colorName.replace("-claro", "")}.png`;
        }

        // PAÑOLETA
        if (productName.includes("pañoleta") || productName.includes("panoleta") || productName.includes("paoleta")) {
            let c = colorName.replace('-claro', '').replace('-noche', '');
            if (identidad === "ejercito") return isBack ? `/static/img/prendas/ejercito/pañoletas/detras.png` : `/static/img/prendas/ejercito/pañoletas/panoleta_${c}.png`;
            if (identidad === "policia") return isBack ? `/static/img/prendas/Policia/pañoletas/detras.png` : `/static/img/prendas/Policia/pañoletas/${c}.png`;
            if (identidad === "gaula") return isBack ? `/static/img/prendas/gaula/Pañoletas/detras.png` : `/static/img/prendas/gaula/Pañoletas/panoleta_${c}.png`;
            if (identidad === "armada") return isBack ? `/static/img/prendas/armada/pañoleta/detras.png` : (colorName === "verde" || colorName === "verde-claro" ? `/static/img/prendas/armada/pañoleta/pañoleta verde .png` : `/static/img/prendas/armada/pañoleta/panoleta_${c}.png`);
        }
        
        // RH
        if (productName === "rh") {
            const sign = state.modeloRh || "O+";
            if (identidad === "ejercito") {
                const rhMap = {
                    "A+": "A+ verde.png",
                    "A-": "A- verde.png",
                    "AB+": "AB+ verde .png",
                    "AB-": "AB- verde.png",
                    "B+": "B+ verde .png",
                    "B-": "B- verde.png",
                    "O+": "O+ verde.png",
                    "O-": "O- verde.png"
                };
                return `/static/img/prendas/ejercito/Rh/${rhMap[sign] || 'O+ verde.png'}`;
            }
            if (identidad === "policia") {
                const bg = colorName === 'azul-noche' ? 'azul' : colorName;
                
                // Mapeo detallado de archivos que s existen en la carpeta de la Polica:
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
            if (identidad === "gaula") {
                const gaulaRhMap = {
                    "A+platiado": "A+rhgris.png",
                    "A+verde-claro": "A+rhverde.png",
                    "A-platiado": "A-gris-rh.png",
                    "A-verde-claro": "A-verde-rh.png",
                    "AB+platiado": "AB+.png",
                    "AB+verde-claro": "AB+verde.rh.png",
                    "AB-platiado": "AB-gris_rh.png",
                    "AB-verde-claro": "AB-rh,verde.png",
                    "B+platiado": "B+gris.png",
                    "B+verde-claro": "B+verde.png",
                    "B-platiado": "B-rh_gris.png",
                    "B-verde-claro": "B-rh-verde.png",
                    "O+platiado": "O+grisrh.png",
                    "O+verde-claro": "O+verde_rh.png",
                    "O-platiado": "O-rh-gris.png",
                    "O-verde-claro": "O-verde,rh.png"
                };
                const key = sign + color;
                if (gaulaRhMap[key]) {
                    return `/static/img/prendas/gaula/Rh/${gaulaRhMap[key]}`;
                }
                return `/static/img/prendas/gaula/Rh/rh_defrente.png`;
            }
            if (identidad === "armada") {
                if (isBack) return `/static/img/prendas/armada/Rh/espaldar.png`;
                const armadaRhMap = {
                    "A+": "A+rh .png",
                    "A-": "A- rh.png",
                    "AB+": "AB+ rh .png",
                    "AB-": "AB- rh.png",
                    "B+": "B+rh .png",
                    "B-": "B- rh.png",
                    "O+": "O+rh.png",
                    "O-": "O- rh.png"
                };
                return `/static/img/prendas/armada/Rh/${armadaRhMap[sign] || 'O+rh.png'}`;
            }
        }
        
        // PRESILLAS
        if (productName === "presillas" || productName === "presilla") {
            const rankStr = (state.modeloPresilla || "coronel").toLowerCase().trim();
            if (identidad === "policia") {
                const colorStr = colorName === 'azul-noche' ? 'azul noche' : colorName;
                const policiaPresillaMap = {
                    "brigadier general azul noche": "brigadier general azul noche.png",
                    "brigadier general dorado": "brigadier general dorado .png",
                    "capitan azul noche": "capitan azul noche .png",
                    "capitan dorado": "capitan dorado.png",
                    "coronel azul noche": "coronel azul noche .png",
                    "coronel dorado": "coronel dorado.png",
                    "general azul noche": "general azul noche.png",
                    "general dorado": "general dorado.png",
                    "mayor azul noche": "mayor azul noche .png",
                    "mayor dorado": "mayor dorado.png",
                    "mayor general dorado": "mayor general dorado.png",
                    "mayor general azul noche": "mayor general.png",
                    "subintendente azul noche": "subitendente azul noche.png",
                    "subteniente dorado": "subteniente dorado.png",
                    "teniente azul noche": "teniente azul noche .png",
                    "teniente coronel azul noche": "teniente coronel azul noche  .png",
                    "teniente coronel dorado": "teniente coronel dorado.png",
                    "teniente dorado": "teniente dorado.png"
                };
                const key = rankStr + " " + colorStr;
                const filename = policiaPresillaMap[key];
                if (filename) {
                    return `/static/img/prendas/Policia/presilla/${filename}`;
                }
                return `/static/img/prendas/Policia/presillas/presilla_policia.png`;
            } else if (identidad === "ejercito") {
                return `/static/img/prendas/ejercito/presillas/presilla_ejercito.png`;
            } else if (identidad === "gaula") {
                return `/static/img/prendas/gaula/presillas/presilla_gaula.png`;
            }
        }

        // GAFETE
        if (productName.includes("gafete")) {
            if (identidad === "policia") {
                return isBack ? `/static/img/prendas/Policia/gafete%20del%20nombre%20o%20apellido/respalda-gafete.png` : `/static/img/prendas/Policia/gafete%20del%20nombre%20o%20apellido/${colorName === 'azul-noche' ? 'azul' : 'verde'}-gafete.png`;
            } else if (identidad === "ejercito" || identidad === "armada" || identidad === "gaula") {
                let escC = colorName;
                if (escC.includes('verde')) escC = 'verde';
                let baseDir = '';
                if (identidad === "armada") {
                    baseDir = `/static/img/prendas/armada/gafete del nombre o apellido`;
                    if (escC === 'verde') return isBack ? `${baseDir}/espaldar.png` : `${baseDir}/gafete verde.png`;
                    return isBack ? `${baseDir}/espaldar.png` : `${baseDir}/frente.png`; // Fallback for other colors
                }
                else if (identidad === "gaula") {
                    baseDir = `/static/img/prendas/gaula/gafete del nombre o apellido`;
                    if (escC === 'verde') return isBack ? `${baseDir}/reves-gafete.png` : `${baseDir}/verde.png`;
                }
                else {
                    baseDir = `/static/img/prendas/ejercito/gafete del nombre o apellido`;
                    if (escC === 'verde') return isBack ? `${baseDir}/reves-gafete.png` : `${baseDir}/gafete verde.png`;
                    return isBack ? `${baseDir}/reves-gafete.png` : `${baseDir}/frente.png`;
                }
                
                return isBack ? `${baseDir}/reves-gafete.png` : `${baseDir}/${escC}.png`;
            }
            return null; // Otras fuerzas no tienen gafete coloreado
        }
        
        return null;
    }

    function getColorHex(colorName) {
        // Mapeo de nombres de color a cdigos hexadecimales
        const colorHexMap = {
            blanco: "#ffffff",
            negro: "#000000",
            "verde-claro": "#2D5016",
            beiches: "#D3C0A3",
            dorado: "#e6f141",
            cafe: "#424215",
            "azul-noche": "#192857",
            platiado: "#C0C0C0"
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

        // Formatear mes/ao
        let contingenciaFmt = state.anoContingencia ? state.anoContingencia : "Pendiente";
        
        // Crear descripcion completa con TODOS los pasos
        let modeloTxt = "";
        if (state.producto === "rh" && state.modeloRh) {
            modeloTxt = ` | Tipo de Sangre: ${state.modeloRh}`;
        } else if ((state.producto === "presillas" || state.producto === "presilla") && state.modeloPresilla) {
            modeloTxt = ` | Rango: ${state.modeloPresilla}`;
        }
        
        const isEspecial = ["rh", "presillas", "gafete", "gafete del nombre o apellido", "pañoleta", "paoleta", "panoleta", "paÃ±oleta", "gorra"].includes((state.producto || "").toLowerCase());
        
        let descripcionCompleta = `${identidad}`;
        
        // El buso manga larga y el buso no llevan la tÃ©cnica (por ser sublimados por defecto)
        const esMangaBusoOnly = ["buso", "buso-manga-larga", "buso_manga_larga", "buso manga larga"].includes((state.producto || "").toLowerCase());
        const esCualquierBuso = ["buso", "buso-manga-larga", "buso_manga_larga", "buso manga larga", "buso_tactico", "buso tactico", "buso-tactico"].includes((state.producto || "").toLowerCase());
        
        // La tecnica (bordado/impresion) la llevan todos EXCEPTO los busos manga larga y el buso (y en gorras sÃ­)
        if (!esMangaBusoOnly) {
            descripcionCompleta += ` | ${tecnica}`;
        }
        
        if (!isEspecial && !esCualquierBuso) {
            descripcionCompleta += ` | ${contingenciaFmt}`;
        }
        
        descripcionCompleta += ` | ${producto}${modeloTxt} | Color: ${color}`;
        
        if (!isEspecial) {
            descripcionCompleta += ` | Talla: ${talla}`;
        }
        
        // El estampado s aplica a paoletas y se quita para otros especiales, lo definimos ac:
        const llevaEstampado = !["rh", "presillas", "gafete", "gafete del nombre o apellido"].includes((state.producto || "").toLowerCase());
        
        // Agregar a la descripcionCompleta SOLO si ya eligio un estampado
        if (llevaEstampado && state.estampado) {
            descripcionCompleta += ` | Estampado: ${estampado}`;
        }

        // Ocultar Talla, Contingencia y Estampado del panel derecho si no aplican 
        let pTal = document.getElementById("preview-talla");
        if (pTal && pTal.parentElement) {
            pTal.parentElement.style.display = isEspecial ? "none" : "flex";
        }

        let pTecnica = document.getElementById("preview-tecnica");
        
        if (pTecnica && pTecnica.parentElement) {
            pTecnica.parentElement.style.display = esMangaBusoOnly ? "none" : "flex";
        }
        
        let pIdentidad = document.getElementById("preview-identidad");
        if (pIdentidad) pIdentidad.textContent = formatLabel(state.identidad);
        if (pTecnica) pTecnica.textContent = esMangaBusoOnly ? "No aplica" : tecnica;

        let pEst = document.getElementById("preview-estampado");
        if (pEst && pEst.parentElement) {
            pEst.parentElement.style.display = (isEspecial && (state.producto || "").toLowerCase() !== "gorra" && (state.producto || "").toLowerCase() !== "pa\u00f1oleta" && (state.producto || "").toLowerCase() !== "panoleta") ? "none" : "flex";
        }
        // Actualizar panel derecho (vista previa)
        if (productoInfoPreview) productoInfoPreview.textContent = producto;
        
        // Mostrar color con cuadro de color
        if (colorInfoPreview) {
            if (state.pasoActual === 3 || state.pasoActual === 4 || state.pasoActual === 5) {
                const colorHex = getColorHex(state.color) || "#cccccc";
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
            estampadoInfoPreview.textContent = state.estampado ? estampado : "No aplica";
            const filaEstampado = estampadoInfoPreview.parentElement;
            if (filaEstampado && filaEstampado.classList.contains('info-item')) {
                filaEstampado.style.display = (!llevaEstampado || !state.estampado) ? 'none' : 'flex';
            }
        }
        
        if (tallaInfoPreview) {
            tallaInfoPreview.textContent = isEspecial ? "No aplica" : (state.talla || "Pendiente");
            const filaTalla = tallaInfoPreview.parentElement;
            if (filaTalla && filaTalla.classList.contains('info-item')) {
                // Ocultar si es especial, O si la talla no ha sido seleccionada aÃºn (talla es vacÃ­a o null)
                filaTalla.style.display = (isEspecial || !state.talla) ? 'none' : 'flex';
            }
        }
        if (precioInfoPreview) precioInfoPreview.textContent = priceMap[state.producto] || "$ 45.000";
        if (descripcionInfoPreview) descripcionInfoPreview.textContent = descripcionCompleta;
        
        // Actualizar identidad y tcnica
        const identidadPreview = document.getElementById("preview-identidad");
        const tecnicaPreview = document.getElementById("preview-tecnica");
        if (identidadPreview) identidadPreview.textContent = identidad;
        if (tecnicaPreview) tecnicaPreview.textContent = tecnica;

        // Mostrar preview con imagen del producto o cono
        // En Paso 3 o superior, mostrar la imagen con el color seleccionado
        // Mapeo de colores a cdigos hexadecimales
        function getColorHex(colorName) {
            const hexMap = {
                "blanco": "#ffffff",
                "negro": "#151515",
                "verde-claro": "#4d5b3c", // verde oliva
                "beiches": "#d5caac", // beige claro
                "dorado": "#d4af37",
                "cafe": "#4a3c31",
                "azul-noche": "#1a242f",
                "platiado": "#C0C0C0"
            };
            return hexMap[colorName] || "#cccccc";
        }
        
        let imagen = null;
        const p = (state.producto || "").toLowerCase();
        
        // Mostrar imagen a color SOLO si estamos en el paso 3 o superior, y hay color seleccionado.
        if (state.pasoActual >= 3 && state.color) {
            if (p === "rh" && !state.modeloRh) {
                imagen = getProductImage(); // Si es RH falta el modelo, mostrar base
            } else if ((p === "presillas" || p === "presilla") && !state.modeloPresilla) {
                imagen = getProductImage(); // Si es Presilla falta el modelo, mostrar base
            } else {
                imagen = getProductColorImage(state.color);
            }
        }

        // Si no hay imagen definida (por estar en paso < 3 o no tener color), usar la imagen base/molde
        if (!imagen) {
            // Para pañoletas, si estamos en paso 3 y no hay color, no mostrar nada
            if (["pañoleta", "paÃ±oleta", "panoleta", "paoleta"].includes(p) && state.pasoActual >= 3 && !state.color) {
                imagen = ""; // Sin imagen
            } else {
                // En pasos 1 y 2, o si es otro producto, mostrar siempre el boceto/molde
                imagen = getProductImage();
            }
        }
        
        if (imagen) {

        // Siempre crear o actualizar el preview-container
        // Aumentar un poco el tamaÃ±o si es un accesorio pequeÃ±o como Gafetes, RH o Presillas
        let scaleStyle = "";
            const isGafete = state.producto === "gafete del nombre o apellido" || state.producto === "gafete";
            const isGorra = state.producto === "gorra";
            const isRh = state.producto === "rh";
            const isSmallItem = isRh || state.producto === "presillas";
            
            if (isGafete || isRh) {
                scaleStyle = "transform: scale(1.3);";
            } else if (isSmallItem) {
                scaleStyle = "transform: scale(1.3);";
            }

            let existingContainer = preview.querySelector("#preview-container");
            
            if (!existingContainer) {
                preview.innerHTML = `
                    <div id="preview-container" style="position: relative; text-align: center; background: white; width: 100%; height: 500px; display: flex; justify-content: center; align-items: center; overflow: hidden; border-radius: 8px;">
                        <style>
                            #imagen-producto {
                                width: 100%;
                                height: 100%;
                                max-width: 500px;
                                max-height: 500px;
                                object-fit: contain;
                                transition: transform 0.2s ease-in-out;
                                z-index: 1;
                                display: block;
                            }
                            #imagen-producto:hover {
                                transform: scale(1.15);
                            }
                            @media (max-width: 768px) {
                                #imagen-producto {
                                    max-width: 300px;
                                }
                            }
                        </style>
                        <img id="imagen-producto" src="" alt="Vista Previa">
                        <div id="gafete-overlay" style="display: none; position: absolute; top: 36%; left: 50%; transform: translate(-50%, -50%) scale(1.3); text-align: center; width: 90%; color: #000; font-family: Arial, sans-serif; white-space: nowrap; z-index: 5; flex-direction: column; align-items: center; justify-content: center; background: transparent; padding: 0;">
                            <div id="overlay-rango" style="font-size: 14px; font-weight: 600; margin-bottom: 2px; line-height: 1;"></div>
                            <div id="overlay-nombre" style="font-size: 22px; font-weight: 900; text-transform: uppercase; letter-spacing: 0.5px; line-height: 1;"></div>
                        </div>
                        <div id="rh-overlay" style="display: none; position: absolute; top: 45%; left: 50%; transform: translate(-50%, -50%) scale(1.5); text-align: center; color: #000; font-family: 'Arial Black', Arial, sans-serif; white-space: nowrap; z-index: 5; font-size: 18px; font-weight: 900; text-shadow: 1px 1px 2px rgba(255,255,255,0.4); background: transparent; padding: 0;">
                        </div>
                        <img id="rango-overlay-img" src="" style="display: none; position: absolute; max-width: 40px; max-height: 40px; top: 38%; left: 60%; z-index: 6; transform: translate(-50%, -50%);">
                    </div>
                `;
            }
            
            let imgEl = preview.querySelector("#imagen-producto");
            if (imagen) {
                imgEl.src = imagen;
                imgEl.alt = state.producto || 'Vista Previa de Prenda';
                imgEl.onerror = function() {
                    // Fallback si la imagen de color especfico no existe
                    const fallbackImg = getProductImage();
                    if (this.src !== window.location.origin + fallbackImg && fallbackImg) {
                        this.src = fallbackImg;
                    } else {
                        this.style.display = 'none';
                    }
                };
                imgEl.style.display = 'block';
            } else {
                imgEl.style.display = 'none';
            }
            
            if (isGafete || isRh) { imgEl.style.transform = "scale(1.3)"; } else if (isSmallItem) { imgEl.style.transform = "scale(1.3)"; } else { imgEl.style.transform = "none"; }
            
        let overlayEl = preview.querySelector("#gafete-overlay");
        let rhOverlayEl = preview.querySelector("#rh-overlay");
        let rangoOverlayImg = preview.querySelector("#rango-overlay-img");

        // Ocultar ambos por defecto
        if (overlayEl) overlayEl.style.display = "none";
        if (rhOverlayEl) rhOverlayEl.style.display = "none";
        if (rangoOverlayImg) rangoOverlayImg.style.display = "none";

            if (isRh && state.vistaPrenda !== "trasera") {
                if (rhOverlayEl && state.modeloRh) {
                    // Para el ejercito y gaula ocultamos el texto porque las imgenes ya lo traen horneado
                    if (state.identidad === "ejercito" || state.identidad === "gaula") {
                        rhOverlayEl.style.display = "none";
                    } else {
                        rhOverlayEl.style.display = "block";
                    }
                    
                    let txtSangre = state.modeloRh || "";
                    if (txtSangre.includes("+")) txtSangre = txtSangre.replace("+", " POS");
                    if (txtSangre.includes("-")) txtSangre = txtSangre.replace("-", " NEG");
                    
                    if (state.identidad === "policia" && (state.color === "azul-noche" || state.color === "negro")) {
                        rhOverlayEl.style.color = "#ccff00"; 
                        rhOverlayEl.style.textShadow = "-1px -1px 0 #0d1b2a, 1px -1px 0 #0d1b2a, -1px 1px 0 #0d1b2a, 1px 1px 0 #0d1b2a";
                    } else if (state.identidad === "policia" && state.color === "verde-claro") {
                        rhOverlayEl.style.color = "#d0d6c0"; 
                        rhOverlayEl.style.textShadow = "-1px -1px 0 #394524, 1px -1px 0 #394524, -1px 1px 0 #394524, 1px 1px 0 #394524";
                    } else {
                        rhOverlayEl.style.color = "#000000"; 
                        rhOverlayEl.style.textShadow = "none";
                    }

                    rhOverlayEl.textContent = txtSangre.toUpperCase();
                }
            }
        else if (isGafete && state.vistaPrenda !== "trasera") {
                overlayEl.style.display = "flex";

                // Determinar colores basados en la seleccin o en la imagen mostrada
                let textColor = "#000000"; // Negro por defecto para la mayora de fuerzas
                let shadowColor = "transparent"; // Sin sombra por defecto  
                let topPosition = "50%";
                
                if (state.identidad === "policia") {
                    // La Polica usa texto con estilo "nen"
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
                    // Ejrcito, Gaula y Armada usan texto con efecto de bordado oscuro
                    if (state.identidad === "ejercito") {
                        textColor = "#1e2b14"; // Verde oliva muy oscuro
                        shadowColor = "rgba(0,0,0,0.8)";
                        topPosition = "50%";
                    } else {
                        textColor = "#000000"; // Negro puro para max contraste
                        shadowColor = "transparent"; // Sin sombra gruesa para conservar la tipografia
                        topPosition = "52%";
                    }
                }

                overlayEl.style.top = topPosition;
                overlayEl.style.color = textColor;
                
                const shadowVal = (state.identidad === "ejercito") 
                    ? `-1px -1px 0 rgba(0,0,0,0.6), 1px -1px 0 rgba(0,0,0,0.6), -1px 1px 0 rgba(0,0,0,0.6), 1px 1px 0 rgba(0,0,0,0.6), 1px 1px 2px rgba(0,0,0,0.8), -1px -1px 1px rgba(255,255,255,0.2)`
                    : (shadowColor !== "transparent" 
                        ? `-1px -1px 0 ${shadowColor}, 1px -1px 0 ${shadowColor}, -1px 1px 0 ${shadowColor}, 1px 1px 0 ${shadowColor}` 
                        : 'none');
                
                // Aplicar estilos
                const divRango = preview.querySelector("#overlay-rango");
                const divNombre = preview.querySelector("#overlay-nombre");
                if (state.identidad === "ejercito") {
                    divNombre.style.fontFamily = "'Arial Black', sans-serif";
                    divRango.style.fontFamily = "'Arial Black', sans-serif";
                    divNombre.style.letterSpacing = "1.5px";
                    divNombre.style.fontWeight = "900";
                    divNombre.style.fontSize = "24px";
                    divNombre.style.transform = "scaleY(1.1)"; // Ligeramente estirado verticalmente
                    divNombre.style.webkitTextStroke = "0px";
                    divRango.style.webkitTextStroke = "0px";
                    divNombre.style.order = "2";
                    divRango.style.order = "1";
                } else {
                    // Policia, Gaula y Armada usan la misma tipografia de gafetes
                    divNombre.style.fontFamily = "'Arial Rounded MT Bold', 'Helvetica Rounded', Arial, sans-serif";
                    divRango.style.fontFamily = "'Arial Rounded MT Bold', 'Helvetica Rounded', Arial, sans-serif";
                    divNombre.style.letterSpacing = "0.5px";
                    divNombre.style.fontWeight = "900";
                    divNombre.style.fontSize = "22px";
                    divNombre.style.transform = "none";
                    divRango.style.transform = "none";
                    divNombre.style.webkitTextStroke = "0px";
                    divRango.style.webkitTextStroke = "0px";
                    divNombre.style.order = "2";
                    divRango.style.order = "1";
                }
                

                // Ajuste proporcional de tamaÃ±os para que sean equitativos y encajen y centrados
                divRango.style.fontWeight = "800";
                divRango.style.color = textColor;
                divRango.style.textShadow = shadowVal;
                divRango.style.textAlign = "center";
                divRango.style.width = "100%";
                divRango.style.margin = "0 0 1px 0"; // Mueve el rango un toque para separarlo
                divRango.style.padding = "0";
                
                divNombre.style.fontWeight = "900";
                divNombre.style.color = textColor;
                divNombre.style.textShadow = shadowVal;
                divNombre.style.textAlign = "center";
                divNombre.style.width = "100%";
                divNombre.style.margin = "0";
                divNombre.style.padding = "0";
                
                const rangoFinal = state.rango ? state.rango.charAt(0).toUpperCase() + state.rango.slice(1).toLowerCase() : 'Rango'; 
                let nombreFinalRaw = state.nombre ? state.nombre.toUpperCase().trim() : 'NOMBRE';
                
                // LÃ³gica de EjÃ©rcito: Solo Apellido
                const identId = state.identidad ? state.identidad.toLowerCase().trim() : '';
                if (identId === 'ejercito' && nombreFinalRaw !== 'NOMBRE') {
                    let partes = nombreFinalRaw.split(/\s+/);
                    if (partes.length === 2) {
                        nombreFinalRaw = partes[1]; 
                    } else if (partes.length === 3) {
                        nombreFinalRaw = partes[2]; 
                    } else if (partes.length >= 4) {
                        nombreFinalRaw = partes[2]; // Primer apellido usualmente en 4 palabras
                    }
                }
                
                const nombreFinal = nombreFinalRaw;

                                if (identId === 'ejercito') {
                    divRango.style.display = 'none';
                    divNombre.style.marginBottom = '2px'; // adjust spacing
                } else {
                    divRango.style.display = 'block';
                    divRango.textContent = rangoFinal;
                }
                divNombre.textContent = nombreFinal;
                
                // Escalar el nombre para que quepa bien y sea centrar
                let baseNombreSize = identId === 'ejercito' ? 28 : 26;
                let maxCharsNombre = identId === 'ejercito' ? 8 : 10;
                
                if (identId === 'ejercito') {
                    // Hacer el parche del gafete un poco mÃ¡s grande y bajarlo ligeramente si el contenedor lo permite
                    imgEl.style.transform = "scale(1.6)";
                    overlayEl.style.transform = "translate(-50%, -50%) scale(1.6)";
                } else {
                    imgEl.style.transform = "scale(1.3)";
                    overlayEl.style.transform = "translate(-50%, -50%) scale(1.3)";
                }

                if (nombreFinal.length > maxCharsNombre) {
                    let newFontSize = (baseNombreSize * maxCharsNombre) / nombreFinal.length;
                    divNombre.style.fontSize = Math.max(5, newFontSize) + "px";
                } else {
                    divNombre.style.fontSize = baseNombreSize + "px";
                }
                
                // Escalar el rango para que sea equitativo y mas pequeÃ±o y centrado
                let baseRangoSize = identId === 'ejercito' ? 5 : 14;
                let maxCharsRango = identId === 'ejercito' ? 18 : 12;
                if (rangoFinal.length > maxCharsRango) {
                    let newRangoSize = (baseRangoSize * maxCharsRango) / rangoFinal.length;
                    divRango.style.fontSize = Math.max(3.5, newRangoSize) + "px";
                } else {
                    divRango.style.fontSize = baseRangoSize + "px";
                }

            } else {
                overlayEl.style.display = "none";
            }
            if (!isRh || state.vistaPrenda === "trasera") {
                if (rhOverlayEl) rhOverlayEl.style.display = "none";
            }

            // LÃ³gica del OVERLAY para RANGOS en Busos y Gorras:
            const esMuestraDistintivo = (esCualquierBuso || isGorra) && state.estampado && state.estampado.startsWith("distintivos - ") && state.vistaPrenda !== "trasera";
            if (esMuestraDistintivo) {
                // Limpiar el String "distintivos - Coronel" -> "Coronel"
                const rangoStr = state.estampado.replace("distintivos - ", "").trim();
                const identId = state.identidad ? state.identidad.toLowerCase().trim() : "policia";
                
                if (rangoStr && rangoStr !== "(seleccionar)" && rangoStr !== "Pendiente") {
                    // Ej: "Coronel" -> "coronel", "Mayor General" -> "mayor_general"
                    let rangoFormat = rangoStr.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
                    rangoFormat = rangoFormat.replace(/\s*\/\s*/g, " "); // espacios mantenidos
                    
                    if (isGorra) {
                        // Para las gorras, las imÃ¡genes de rangos no son overlays pequeÃ±os, son LA GORRA COMPLETA con el rango.
                        // Entonces, reemplazamos la imagen principal de la prenda y ocultamos el overlay.
                        if (identId === "policia" && !rangoFormat.includes("azul") && !rangoFormat.includes("verde")) {
                            if (state.color === "azul-noche" || state.color === "negro" || !state.color) {
                                rangoFormat += " azul";
                            } else if (state.color === "verde-claro") {
                                rangoFormat += " verde";
                            }
                        } else if (identId === "gaula") {
                            // En Gaula la carpeta es "gorras" en vez de "gorra". AdemÃ¡s, hay espacios raros en algunos archivos.
                            let baseName = rangoFormat.trim();
                            if (state.color === "verde-claro") {
                                // Maps for green distinctives
                                const mappingGaula = {
                                    "brigadier general": "brigadier general verde",
                                    "capitan": "capitan verde",
                                    "coronel": "coronel verde ",
                                    "general": "general  verde",
                                    "intendente jefe": "intendente jefe verde ",
                                    "intendente": "intendente verde",
                                    "mayor general": "mayor general verde",
                                    "mayor": "mayor verde ",
                                    "subcomisario": "subcomisario verde",
                                    "subintendente": "subintendente verde",
                                    "teniente coronel": "teniente coronel verde"
                                    // comisario y subteniente no tienen "verde" en el nombre del archivo
                                };
                                if (mappingGaula[baseName]) {
                                    rangoFormat = mappingGaula[baseName];
                                }
                            } else if (state.color === "negro") {
                                // Maps for black distinctives
                                const mappingGaulaNegro = {
                                    "brigadier general": "brigadier general negro ",
                                    "capitan": "capitan negro",
                                    "comisario": "comisario negro",
                                    "coronel": "coronel negro",
                                    "intendente jefe": "intendente jefe negro",
                                    "intendente": "intendente negro",
                                    "mayor general": "mayor general negro",
                                    "mayor": "mayor negro",
                                    "subcomisario": "subcomisario negro",
                                    "subintendente": "subintendente negro",
                                    "subteniente": "subteniente negro",
                                    "teniente coronel": "teniente coronel negro ",
                                    "teniente": "teniente negro"
                                };
                                if (mappingGaulaNegro[baseName]) {
                                    rangoFormat = mappingGaulaNegro[baseName];
                                }
                            }
                        }
                        
                        let basePathFolder = identId === "gaula" ? "gorras" : "gorra";
                        const gorraRangoSrc = `/static/img/estampados/${identId}/${basePathFolder}/Distintivos/${rangoFormat}.png`;
                        imgEl.src = gorraRangoSrc;

                        let fallbackFallbackSrc = "";
                        if (identId === "ejercito") {
                            fallbackFallbackSrc = `/static/img/prendas/ejercito/gorras/gorra-frente.png`;
                        } else if (identId === "armada") {
                            fallbackFallbackSrc = `/static/img/prendas/armada/gorra/frente-armada.png`;
                        } else {
                            fallbackFallbackSrc = `/static/img/prendas/${identId}/gorras/gorra_${(state.color === 'negro' ? 'negra' : (state.color === 'azul-noche' ? 'azul' : 'verde'))}.png`;
                        }

                        imgEl.onerror = function() {
                            if (!this.src.endsWith(fallbackFallbackSrc)) {
                                this.src = fallbackFallbackSrc;
                            }
                            this.onerror = null; // evitar loops
                        };
                        
                        // Agregar CSS para que la imagen que tiene fondo blanco gigante se vea bien:
                        imgEl.style.mixBlendMode = "multiply"; // Quita el fondo blanco si el contenedor tiene un fondo claro
                        
                        if (rangoOverlayImg) rangoOverlayImg.style.display = "none";

                    } else if (identId === "armada" && productName === "guerrera") {
                        // Armada uses a composite image for distinctive and gafete
                        if (state.estampado && state.estampado.startsWith("distintivos")) {
                             const escImgSrc = `/static/img/estampados/armada/distintivos/distintivo.png`;
                             
                             if (rangoOverlayImg) {
                                  rangoOverlayImg.src = escImgSrc;
                                  rangoOverlayImg.style.display = "block";
                                  rangoOverlayImg.style.top = "38%";
                                  rangoOverlayImg.style.left = "40%";
                                  rangoOverlayImg.style.mixBlendMode = "multiply";
                                  rangoOverlayImg.style.transform = "translate(-50%, -50%) scale(1)";
                                  
                                  rangoOverlayImg.onerror = function() {
                                      this.style.display = "none";
                                  };
                             }
                        }
                    } else {
                        // Para los busos seguimos usando el overlay superpuesto
                        let folderDest = "distintivos";
                        const rangoOverlaySrc = `/static/img/estampados/${identId}/${folderDest}/${rangoFormat}.png`;
                        
                        if (rangoOverlayImg) {
                            rangoOverlayImg.src = rangoOverlaySrc;
                            rangoOverlayImg.style.display = "block";
                            rangoOverlayImg.style.top = "38%";
                            rangoOverlayImg.style.left = "60%";
                            rangoOverlayImg.style.mixBlendMode = "multiply";
                            rangoOverlayImg.style.transform = "translate(-50%, -50%) scale(1)";
                            
                            rangoOverlayImg.onerror = function() {
                                this.style.display = "none";
                            };
                        }
                    }
                }
            } else {
                if (rangoOverlayImg) rangoOverlayImg.style.display = "none";
            }

            // ARMADA GUERRERA: GAFETE/DISTINTIVO OVERLAY
            if (state.identidad && state.identidad.toLowerCase().trim() === "armada" && (state.producto || "").toLowerCase() === "guerrera" && state.vistaPrenda !== "trasera") {
                if (state.estampado && (state.estampado === "distintivos" || state.estampado.startsWith("distintivos") || state.estampado === "nombres")) {
                    if (rangoOverlayImg) {
                        const gafColor = state.color === "negro" ? "negro" : "verde";
                        rangoOverlayImg.src = `/static/img/prendas/armada/gafete del nombre o apellido/gafete ${gafColor}.png`;
                        rangoOverlayImg.style.display = "block";
                        rangoOverlayImg.style.top = "38%";
                        rangoOverlayImg.style.left = "70%"; // Right breast pocket for gafete
                        rangoOverlayImg.style.mixBlendMode = "normal";
                        rangoOverlayImg.style.transform = "translate(-50%, -50%) scale(0.35)";
                        
                        rangoOverlayImg.onerror = function() {
                            this.src = `/static/img/prendas/armada/gafete del nombre o apellido/gafete verde.png`;
                            this.onerror = function() {
                                this.style.display = "none";
                            };
                        };
                    }
                }
            }


        // Escudos en paÃ±oletas
        const isPanoleta = ['pañoleta', 'paÃ±oleta', 'panoleta', 'paoleta'].includes((state.producto || '').toLowerCase());
        if (isPanoleta && state.estampado && state.estampado.toLowerCase().startsWith('escudos') && state.vistaPrenda !== 'trasera') {
            // El dropdown solo da options Escudo 1 / Escudo 2. Ajustarlos segÃºn sea la lÃ³gica si tienen archivos  distintos
            // De lo contrario mantenemos la lÃ³gica actual pero mostramos la imÃ¡gen base a color si no hay selecciÃ³n

            const identId = state.identidad ? state.identidad.toLowerCase().trim() : 'policia';
            let escImgSrc = '';
            let c = (state.color || 'verde-claro').replace('-claro', '').replace('-noche', '');

            // Agregar la lÃ³gica para diferentes escudos aquÃ­ si tienes diferentes archivos,
            // por ejemplo para "Escudo 2" usar un archivo diferente.
            // Para mantenerlo sencillo, se usa la imagen de color si escogieron el escudo

            if (identId === 'ejercito') {
                let escC = c;
                if (escC.includes('verde')) escC = 'verde';
                else if (escC.includes('blanco')) escC = 'ejercito';
                else if (escC.includes('negro')) escC = 'negro';
                else if (escC.includes('beiche') || escC.includes('beige')) escC = 'beiches';

                // Si seleccionaron escudo 2, agregar su path si aplica
                if (state.estampado.includes('Estilo 3') || state.estampado.includes('Escudo 3')) {
                     escImgSrc = `/static/img/estampados/ejercito/pañoleta/Escudos/estilo3.png`;
                } else if (state.estampado.includes('Estilo ,3')) {
                     escImgSrc = `/static/img/estampados/ejercito/pañoleta/Escudos/estilo,3.png`;
                } else if (state.estampado.includes('Estilo 2') || state.estampado.includes('Escudo 2')) {
                     escImgSrc = `/static/img/estampados/ejercito/pañoleta/Escudos/estilo2.png`;
                } else if (state.estampado.includes('Estilo ,2')) {
                     escImgSrc = `/static/img/estampados/ejercito/pañoleta/Escudos/estilo,2.png`;
                } else if (state.estampado.includes('Estilo 1') || state.estampado.includes('Escudo 1')) {
                     escImgSrc = `/static/img/estampados/ejercito/pañoleta/Escudos/estilo-1.png`;
                } else if (state.estampado.includes('Estilo -1')) {
                     escImgSrc = `/static/img/estampados/ejercito/pañoleta/Escudos/estilo1.png`;
                } else {
                     // Default
                     escImgSrc = `/static/img/estampados/ejercito/pañoleta/Escudos/estilo-1.png`;
                }
            }
            else if (identId === 'gaula') {
                if (state.color === "negro") {
                    if (state.estampado.includes('Estilo 2') || state.estampado.includes('Escudo 2')) {
                        escImgSrc = `/static/img/estampados/gaula/pañoleta/Escudos/estampado 2.png`;
                    } else {
                        escImgSrc = `/static/img/estampados/gaula/pañoleta/Escudos/estampado 1.png`;
                    }
                } else {
                    if (state.estampado.includes('Estilo 2') || state.estampado.includes('Escudo 2')) {
                        escImgSrc = `/static/img/estampados/gaula/pañoleta/Escudos/estampado2.png`;
                    } else {
                        escImgSrc = `/static/img/estampados/gaula/pañoleta/Escudos/estampado1.png`;
                    }
                }
            }
            else if (identId === 'armada') {
                escImgSrc = `/static/img/estampados/armada/pañoleta/Escudos/${c === 'negro' ? 'negro.png' : 'verde.png'}`;
            }
            else escImgSrc = `/static/img/estampados/Policia/pañoleta/Escudos/pañoleta ${c.includes('azul') ? 'azul' : 'verde'}.png`; 
            
            // En caso que el substring sea vacio o "escudos"
            if (state.estampado.trim().toLowerCase() === "escudos") {
                // Excepto armada, permitimos escudos directamente porque no hay subOpciones.
                if (identId !== 'armada') {
                    escImgSrc = "";
                }
            }
            
            let imgEl2 = preview.querySelector("#imagen-producto");
            if (imgEl2 && escImgSrc) {
                imgEl2.src = escImgSrc;
            }
            
            let muestraPanoleta = preview.querySelector("#estampado-panoleta");
            if (muestraPanoleta) muestraPanoleta.style.display = "none";
            
        } else {
            let muestraPanoleta = preview.querySelector("#estampado-panoleta");
            if (muestraPanoleta) muestraPanoleta.style.display = "none";
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
                if ((state.producto === "presillas" || state.producto === "presilla") && !state.modeloPresilla) {
                    alert("?? Por favor selecciona un Rango");
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
            
            // Lgica para el botn del paso 3
            if (btnPasos3) {
                const prendasTerminanPaso3 = ["rh", "gafete del nombre o apellido", "gafete", "presillas", "buso", "buso-manga-larga"];
                const isGorraEjercito = productoActual === "gorra" && state.identidad && state.identidad.toLowerCase() === "ejercito";
                if (prendasTerminanPaso3.includes(productoActual) || isGorraEjercito) {
                    btnPasos3.textContent = "Finalizar";
                } else {
                    btnPasos3.textContent = "Siguiente";
                }
            }
            
            // Lgica para el botn del paso 4
            if (btnPasos4) {
                const prendasTerminanPaso4 = ["paoleta", "gorra"];
                if (prendasTerminanPaso4.includes(productoActual)) {
                    btnPasos4.textContent = "Finalizar";
                } else {
                    btnPasos4.textContent = "Siguiente";
                }
            }
        }
        // Al retroceder, limpiar los estados de los pasos futuros para que vuelva al estado en que estaba
        if (step < state.pasoActual) {
            if (step === 3) {
                // De 4 a 3: limpiamos el estampado
                state.estampado = null;
                const dropdownDist = document.getElementById("dropdown-distintivos-container");
                if (dropdownDist) dropdownDist.style.display = "none";
                const selectDist = document.getElementById("select-distintivo");
                if (selectDist) selectDist.value = "";
                
                const dropdownEsc = document.getElementById("dropdown-escudos-container");
                if (dropdownEsc) dropdownEsc.style.display = "none";
                const selectEsc = document.getElementById("select-escudo");
                if (selectEsc) selectEsc.value = "";
                
                document.querySelectorAll("[data-estampado]").forEach(btn => btn.classList.remove("seleccionada"));
            } else if (step === 2) {
                // De 3 a 2: limpiamos color, rh, talla, vista
                state.color = null;
                state.estampado = null;
                state.modeloRh = null;
                state.modeloPresilla = null;
                document.querySelectorAll("[data-color]").forEach(btn => btn.classList.remove("seleccionada"));
            } else if (step === 1) {
                // De 2 a 1: limpiamos producto y lo que sigue
                state.producto = null;
                state.color = null;
                state.estampado = null;
                state.modeloRh = null;
                state.modeloPresilla = null;
                document.querySelectorAll("[data-producto]").forEach(btn => btn.classList.remove("seleccionada"));
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
                        infoProducto.style.display = 'none'; // o block si el panel derecho est oculto de todos modos
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
            console.error("Error en validacin de paso:", error);
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
        const prendasEspeciales = ["presillas", "rh", "paoleta", "pañoleta", "paÃ±oleta", "panoleta", "gorra", "contingencia", "gafete del nombre o apellido"];
        const productoActualName = (state.producto || "").toLowerCase();
        const esProductoEspecial = prendasEspeciales.some(p => p.toLowerCase() === productoActualName);

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

        // Establecer la pestaa activa por defecto segn el producto
        tabs.forEach((tab) => {
            tab.classList.remove("activa");
            if (tab.dataset.area === defaultActiveArea && tab.style.display !== "none") {
                tab.classList.add("activa");
            }
        });

        // Habilitar todas las tcnicas para todos los productos
        const tecnicaButtons = document.querySelectorAll("[data-tecnica]");
        tecnicaButtons.forEach((button) => {
            button.disabled = false;
            button.style.opacity = "1";
            button.style.cursor = "pointer";
        });
    }

    function updateTallaVisibility() {
        const btnSiguiente = document.getElementById("btn-siguiente-paso4");
        // En este caso, el paso 4 es el ltimo y va hacia la confirmacin.
        if (btnSiguiente) btnSiguiente.style.display = "inline-block";
    }

    function updateEstampados() {
        const identidad = state.identidad ? state.identidad.toLowerCase().trim() : "policia";
        
        // Mapeo dinamico para todos los estampados
        const estampadosTipos = ['escudos', 'nombres', 'distintivos', 'parches'];
        
        estampadosTipos.forEach(tipo => {
            const btn = document.querySelector(`[data-estampado="${tipo}"]`);
            if (btn) {
                const producto = state.producto ? state.producto.toLowerCase().trim() : "";
                let mostrar = true;

                if (producto === "gorra") {
                    // Para gorras, escudos y parches no aplican
                    if (tipo === "escudos" || tipo === "parches") mostrar = false;
                } else if (identidad === "policia") {
                    if (producto === "pañoleta" || producto === "panoleta" || producto === "paoleta" || producto === "paÃ±oleta" || producto === "pa\u00f1oleta") {
                        if (tipo !== "escudos") mostrar = false; // "las pañolestas solo tienen escudos nada mas"
                    } else if (producto === "guerrera") {
                        if (tipo !== "distintivos" && tipo !== "escudos" && tipo !== "parches") mostrar = false;
                    } else if (producto === "buso-tactico" || producto === "buso_tactico" || producto === "buso tactico") {
                        if (tipo !== "parches" && tipo !== "escudos") mostrar = false;
                    }
                } else if (producto === "paÃ±oleta" || producto === "panoleta" || producto === "paoleta" || producto === "pañoleta") {
                    // Para pañoletas, parches y distintivos no aplican (otras fuerzas)
                    if (tipo === "distintivos" || tipo === "parches") mostrar = false;
                }

                // Ocultar distintivos en todas las secciones para Armada (excepto en guerreras). Para Gaula, solo permitir en gorras. Para Ejército, permitir en guerreras.
                if (identidad === "armada" && tipo === "distintivos" && producto !== "guerrera") {
                    mostrar = false;
                } else if (identidad === "ejercito" && tipo === "distintivos" && producto !== "guerrera") {
                    mostrar = false;
                } else if (identidad === "gaula" && tipo === "distintivos" && producto !== "gorra" && producto !== "guerrera") {
                    mostrar = false;
                }

                btn.style.display = mostrar ? "" : "none";

                const muestra = btn.querySelector('.muestra-color');
                if (muestra) {
                    let imgFolderUrl = "";
                    
                    // Capitalizar la primera letra del tipo para que coincida con la carpeta de forma exacta (Ej: Escudos, Nombres)
                    const carpetaTipo = tipo.charAt(0).toUpperCase() + tipo.slice(1);
                    
                    if (identidad === "ejercito") {
                        if (tipo === "escudos") imgFolderUrl = `url('/static/img/estampados/ejercito/buso tactico/escudo/Escudo_Ejercito_Nacional_de_Colombia.svg.png')`;
                        else if (tipo === "nombres") imgFolderUrl = `url('/static/img/estampados/ejercito/${carpetaTipo}/nombre.png')`; // Ajusta el nombre si difiere
                        else if (tipo === "distintivos") {
                            // Mostrar la misma portada que en la policía
                            imgFolderUrl = `url('/static/img/estampados/policia/gorra/Distintivos/distintivo.png')`;
                        }
                        else if (tipo === "parches") imgFolderUrl = `url('/static/img/estampados/ejercito/buso tactico/parches/Parche_Ejercito.png')`;
                    } else if (identidad === "gaula") {
                        if (tipo === "escudos") imgFolderUrl = `url('/static/img/estampados/gaula/guerrera/escudos/gaula.png')`;
                        else if (tipo === "nombres") imgFolderUrl = `url('/static/img/estampados/gaula/guerrera/nombres/nombre.png')`;
                        else if (tipo === "distintivos") imgFolderUrl = `url('/static/img/estampados/gaula/guerrera/distintivos/distintivo.png')`;
                        else if (tipo === "parches") imgFolderUrl = `url('/static/img/estampados/gaula/guerrera/Parches/parche.png')`;
                    } else if (identidad === "armada") {
                        if (tipo === "escudos") {
                            if (producto === "pañoleta" || producto === "panoleta") {
                                const cc = (state.color || '').toLowerCase();
                                imgFolderUrl = `url('/static/img/estampados/armada/pañoleta/Escudos/${cc === 'negro' ? 'negro.png' : 'verde.png'}')`;
                            } else {
                                imgFolderUrl = `url('/static/img/estampados/armada/buso tactico/escudos/Escudo_Armada_Nacional_de_Colombia.svg.png')`;
                            }
                        }
                        else if (tipo === "nombres") imgFolderUrl = `url('/static/img/estampados/armada/nombres/nombre.png')`;
                        else if (tipo === "distintivos") imgFolderUrl = `url('/static/img/estampados/armada/distintivos/distintivo.png')`;
                        else if (tipo === "parches") imgFolderUrl = `url('/static/img/estampados/armada/parches/armada_parche.png')`;
                    } else { // Policia
                        if (tipo === "escudos") imgFolderUrl = `url('/static/img/estampados/Policia/guerrera/escudos/policia.png')`;
                        else if (tipo === "nombres") imgFolderUrl = `url('/static/img/estampados/Policia/guerrera/nombres/nombre.png')`;
                        else if (tipo === "distintivos") {
                            // Para distintivos de la policía, usar la carátula con barras y laureles dorados
                            imgFolderUrl = `url('/static/img/estampados/policia/gorra/Distintivos/distintivo.png')`; 
                        }
                        else if (tipo === "parches") imgFolderUrl = `url('/static/img/estampados/Policia/guerrera/Parches/parche_policia.png')`;
                    }
                    
                    // Solo actualizamos a la imagen si no da fallback vaco o fallback manual de ser necesario.
                    // Para evitar errores 404, si la imagen no existe simplemente que quede la estructura, pero lo solicitaste para "las fuerzas y todos [los estampados]"
                    muestra.style.backgroundImage = imgFolderUrl;
                    muestra.style.backgroundPosition = "center";
                    muestra.style.backgroundSize = "contain";
                    muestra.style.backgroundRepeat = "no-repeat";
                    muestra.style.backgroundColor = "transparent";
                }
            }
        });
        
        // Manejar opciones especificas de distintivos segÃºn identidad y producto
        const selectDistintivo = document.getElementById("select-distintivo");
        if (selectDistintivo) {
            const producto = state.producto ? state.producto.toLowerCase().trim() : "";
            Array.from(selectDistintivo.options).forEach(opt => {
                if (identidad === "gaula" && producto === "gorra" && (opt.value === "Patrullero" || opt.value === "Teniente")) {
                    opt.style.display = "none";
                    opt.disabled = true;
                    if (state.estampado === "distintivos - " + opt.value) {
                         state.estampado = "distintivos";
                         selectDistintivo.value = "";
                    }
                } else {
                    opt.style.display = "";
                    opt.disabled = false;
                }
            });
        }
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
                "gafete": ["verde-claro"],
                "gafete del nombre o apellido": ["verde-claro"],
                "gorra": ["verde-claro"],
                "guerrera": ["verde-claro"],
                "paoleta": ["verde-claro", "negro", "beiches"],
                "panoleta": ["verde-claro", "negro", "beiches"],
                "pañoleta": ["verde-claro", "negro", "beiches"],
                "presillas": ["dorado", "verde-claro"],
                "rh": ["verde-claro"]
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
                "paoleta": ["verde-claro", "azul-noche"],
                "panoleta": ["verde-claro", "azul-noche"],
                "pañoleta": ["verde-claro", "azul-noche"],
                "presillas": ["dorado", "azul-noche"],
                "rh": ["verde-claro", "azul-noche"]
            },
            "gaula": {
                "buso": ["verde-claro", "blanco", "negro"],
                "buso-tactico": ["negro", "verde-claro"],
                "buso_tactico": ["negro", "verde-claro"],
                "buso-manga-larga": ["blanco", "negro", "verde-claro"],
                "camiseta": ["blanco", "negro", "verde-claro"],
                "gafete": ["verde-claro"],
                "gafete del nombre o apellido": ["verde-claro"],
                "gorra": ["verde-claro", "negro"],
                "guerrera": ["verde-claro"],
                "paoleta": ["verde-claro", "negro"],
                "panoleta": ["verde-claro", "negro"],
                "pañoleta": ["verde-claro", "negro"],
                "presillas": ["verde-claro"],
                "rh": ["verde-claro", "platiado"]
            },
            "armada": {
                "buso": ["verde-claro", "blanco", "negro"],
                "buso-tactico": ["verde-claro", "verde", "negro"],
                "buso_tactico": ["verde-claro", "verde", "negro"],
                "buso tactico": ["verde-claro", "verde", "negro"],
                "buso-manga-larga": ["verde-claro", "negro", "blanco"],
                "buso_manga_larga": ["verde-claro", "negro", "blanco"],
                "rh": ["verde-claro"],
                "gafete": ["verde-claro"],
                "gafete del nombre o apellido": ["verde-claro"],
                "guerrera": ["verde-claro", "verde"],
                "gorra": ["verde-claro", "verde"],
                "paoleta": ["verde-claro", "verde", "negro"],
                "panoleta": ["verde-claro", "verde", "negro"],
                "pañoleta": ["verde-claro", "verde", "negro"]
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
        const esPresillaSinModelo = (producto === "presillas" || producto === "presilla") && !state.modeloPresilla;

        // Aplicar filtrado
        document.querySelectorAll("[data-color]").forEach((btn) => {
            const color = btn.dataset.color;
            const permitido = coloresPermitidos.includes(color);

            if (permitido) {
                btn.style.display = "block";
                
                if (esRhSinModelo || esPresillaSinModelo) {
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
            
            // Mostrar imagen de la prenda si est disponible, sino color slido
            const muestra = btn.querySelector(".muestra-color");
            if (muestra) {
                // Siempre mostrar color slido sin imagen para las opciones de color
                muestra.style.backgroundImage = "none";
                const colorHex = getColorHex(color);
                muestra.style.backgroundColor = colorHex || "#cccccc";
                muestra.style.border = "1px solid #999";
            }
        });
        
        // Si el color actual no es permitido, no seleccionar uno por defecto
        if (coloresPermitidos.length > 0 && !coloresPermitidos.includes(state.color)) {
            state.color = null;
            setActiveClass(document.querySelectorAll("[data-color]"), el => false, "seleccionada");
            updateSummary();
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
        } else if (product === "presillas") {
            htmlVariaciones = `
                <label class="label-opcion" style="display: block; margin-top: 1rem; margin-bottom: 0.5rem; color: #333;">Rango <span class="text-danger">*</span></label>
                <select id="select-modelo-presilla" class="form-control" style="max-width: 300px; margin-bottom: 1rem;">
                    <option value="" disabled selected>Seleccione el rango</option>
                    <option value="General">General</option>
                    <option value="Mayor General">Mayor General</option>
                    <option value="Brigadier General">Brigadier General</option>
                    <option value="Coronel">Coronel</option>
                    <option value="Teniente Coronel">Teniente Coronel</option>
                    <option value="Mayor">Mayor</option>
                    <option value="Capitan">Capitán</option>
                    <option value="Teniente">Teniente</option>
                    <option value="Subteniente">Subteniente</option>
                    <option value="Subitendente">Subintendente</option>
                </select>
            `;
        }

        if (htmlVariaciones) {
            container.style.display = "block";
            // Si el select correcto no existe (RH o Presilla), inyectar HTML de nuevo
            const hasRh = container.querySelector("#select-modelo-rh");
            const hasPresilla = container.querySelector("#select-modelo-presilla");
            if ((product === "rh" && !hasRh) || (product === "presillas" && !hasPresilla)) {
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
                    updateColorAvailability();
                    updateSummary();
                    validarPaso3Realtime();
                };
            }

            const selectPresilla = document.getElementById("select-modelo-presilla");
            if (selectPresilla) {
                if (state.modeloPresilla) {
                    const optionExists = Array.from(selectPresilla.options).some(opt => opt.value === state.modeloPresilla);
                    if (optionExists) {
                        selectPresilla.value = state.modeloPresilla;
                    } else {
                        state.modeloPresilla = null;
                        state.color = null;
                    }
                }

                selectPresilla.onchange = (e) => {
                    state.modeloPresilla = e.target.value;
                    updateColorAvailability();
                    updateSummary();
                    validarPaso3Realtime();
                    
                    // Disparar click en el color actualmente seleccionado si existe, para actualizar la imagen
                    const colorActivo = document.querySelector(".tarjeta-color.seleccionada");
                    if (colorActivo) {
                        colorActivo.click();
                    }
                };
            }
        } else {
            container.style.display = "none";
            container.innerHTML = "";
            state.modeloRh = null;
            state.modeloPresilla = null;
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

        // Validar nombre: solo letras y espacios (incluye acentos y eÃ±es)
        const nombreValido = inputNombre && /^[A-Za-z\u00C0-\u017F\s]+$/.test(inputNombre.value.trim());
        if (!nombreValido) { valid = false; mensajeAlerta += "- Nombre y Apellido (solo letras).\n"; }

        // Validar rango: solo letras y espacios (incluye acentos y eÃ±es)
        const rangoValido = inputRango && /^[A-Za-z\u00C0-\u017F\s]+$/.test(inputRango.value.trim());
        if (!rangoValido) { valid = false; mensajeAlerta += "- Rango (solo letras).\n"; }

        // Validar direccin: cualquier caracter (solo q no est vaco)
        const dirValida = inputDireccion && inputDireccion.value.trim().length > 0;
        if (!dirValida) { valid = false; mensajeAlerta += "- Direccin.\n"; }

        // Validar correo
        const correoValido = inputCorreo && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(inputCorreo.value.trim());
        if (!correoValido) { valid = false; mensajeAlerta += "- Correo Electrnico vlido.\n"; }

        // Validar telfono: solo nmeros
        const telValido = inputTelefono && /^[0-9]+$/.test(inputTelefono.value.trim());
        if (!telValido) { valid = false; mensajeAlerta += "- Telfono (solo nmeros).\n"; }

// Validar Mes y AÃ±o de Contingencia y Talla siempre
        const mesValido2 = inputMesContingencia && inputMesContingencia.value.trim().length > 0;
        const anoValido2 = inputAnoContingencia && inputAnoContingencia.value.trim().length > 0;
        if (!mesValido2) { valid = false; mensajeAlerta += "- Mes de contingencia.\n"; }
        if (!anoValido2) { valid = false; mensajeAlerta += "- AÃ±o de contingencia.\n"; }
        
        const tallaValida2 = inputTalla && inputTalla.value.trim().length > 0;
        if (!tallaValida2 && !state.talla) { valid = false; mensajeAlerta += "- SelecciÃ³n de talla.\n"; }

        // Validar Entidad (Identidad) seleccionada
        if (!state.identidad) { valid = false; mensajeAlerta += "- Seleccionar una Entidad (Ej: Polica, Ejrcito).\n"; }

        // Validar Tcnica seleccionada
        if (!state.tecnica) { valid = false; mensajeAlerta += "- Seleccionar una Tcnica (Ej: Bordado).\n"; }

        // Validar Talla
        // (ya relanzada, pero la validaciÃ³n general de campos no obligarÃ¡ a tallas ni mes de contingencia a menos que sean prendras completas y asÃ­ lo quieras)
        
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
        } else if (state.producto === "presillas" || state.producto === "presilla") {
            camposCompletos = state.color && state.modeloPresilla;
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

        // Validacin en tiempo real para paso 1
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
        
        // Desabilitar el botn inicialmente
        if (btnSiguientePaso1) {
            btnSiguientePaso1.style.opacity = "0.5";
            btnSiguientePaso1.style.cursor = 'pointer';
        }
        
        // Manejar captura de datos personales en paso 1
        if (btnSiguientePaso1) {
            btnSiguientePaso1.addEventListener("click", () => {
                if (!validarPaso1Realtime(true)) {
                    return; // Detener si falta algn campo o es invlido
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
                
                // Forzar la validaciÃ³n aquÃ­
                if (!state.identidad || !state.tecnica) {
                    alert("AsegÃºrate de seleccionar una Entidad y TÃ©cnica.");
                    return;
                }
                
                if (validarPaso(1)) {
                    changeStep(2);
                }
            });
        }

        // Manejar seleccin de identidad pblica
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
                const previoProducto = state.producto;
                state.producto = button.dataset.producto;
                setActiveClass(
                    document.querySelectorAll("[data-producto]"),
                    (element) => element === button,
                    "seleccionada"
                );

                if (previoProducto !== state.producto) {
                    state.estampado = "";
                    document.querySelectorAll("[data-estampado]").forEach(el => el.classList.remove("seleccionada"));
                }

                updateTabsByProduct();
                updateEstampados();
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
                // Permitir seleccionar solo si est visible (display no es none)
                if (window.getComputedStyle(button).display === "none") {
                    return;
                }
                
                if (button.classList.contains("color-deshabilitado")) {
                    if (state.producto === "rh" && !state.modeloRh) {
                        alert("⚠️ Por favor selecciona primero tu Tipo de Sangre.");
                    } else if ((state.producto === "presillas" || state.producto === "presilla") && !state.modeloPresilla) {
                        alert("⚠️ Por favor selecciona primero tu Rango.");
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
                
                // Aplicar color al diseo 3D
                if (window.aplicarColorPrenda) {
                    window.aplicarColorPrenda(state.color);
                }

                // If currently on pañoleta and escudos are shown, update options
                if (['pañoleta', 'paÃ±oleta', 'panoleta', 'paoleta'].includes((state.producto || '').toLowerCase()) && state.estampado.startsWith("escudos")) {
                    const selectEscudo = document.getElementById("select-escudo");
                    if (selectEscudo) {
                        const opt1 = Array.from(selectEscudo.options).find(o => o.value === "Estilo 1");
                        const optM1 = Array.from(selectEscudo.options).find(o => o.value === "Estilo -1");
                        const opt2 = Array.from(selectEscudo.options).find(o => o.value === "Estilo 2");
                        const optC2 = Array.from(selectEscudo.options).find(o => o.value === "Estilo ,2");
                        const opt3 = document.getElementById("opt-escudo-ejercito-3") || Array.from(selectEscudo.options).find(o => o.value === "Estilo 3");
                        const optC3 = document.getElementById("opt-escudo-ejercito-3b") || Array.from(selectEscudo.options).find(o => o.value === "Estilo ,3");
                        
                        if (state.identidad === "ejercito") {
                            if (state.color === "negro") {
                                if (opt1) opt1.style.display = "";
                                if (optM1) optM1.style.display = "";
                                if (opt2) opt2.style.display = "none";
                                if (optC2) optC2.style.display = "none";
                                if (opt3) opt3.style.display = "none";
                                if (optC3) optC3.style.display = "none";
                                selectEscudo.value = "Estilo 1";
                                state.estampado = "escudos - Estilo 1";
                            } else if (state.color === "beiches") {
                                if (opt1) opt1.style.display = "none";
                                if (optM1) optM1.style.display = "none";
                                if (opt2) opt2.style.display = "";
                                if (optC2) optC2.style.display = "";
                                if (opt3) opt3.style.display = "none";
                                if (optC3) optC3.style.display = "none";
                                selectEscudo.value = "Estilo 2";
                                state.estampado = "escudos - Estilo 2";
                            } else if (state.color === "verde-claro") {
                                if (opt1) opt1.style.display = "none";
                                if (optM1) optM1.style.display = "none";
                                if (opt2) opt2.style.display = "none";
                                if (optC2) optC2.style.display = "none";
                                if (opt3) opt3.style.display = "";
                                if (optC3) optC3.style.display = "";
                                selectEscudo.value = "Estilo 3";
                                state.estampado = "escudos - Estilo 3";
                            }
                            updateSummary();
                        } else if (state.identidad === "armada") {
                            // En armada ocultamos los sub-estilos ya que el escImgSrc 
                            // lo armamos segÃºn el color unicamente (verde o negro)
                            if (dropdownEscudosContainer) dropdownEscudosContainer.style.display = "none";
                            state.estampado = "escudos";
                            updateSummary();
                        }
                    }
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

        // Botones de vista delantera/trasera (si tambin hubieran otros que usen la misma clase)
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

        // Botones de navegacin Siguiente/Atrs
        document.getElementById("btn-siguiente-paso2")?.addEventListener("click", () => {
            if (validarPaso(2)) {
                // Verificar si hay prendas que acaban en paso 2 directamente. (no especificado, va a 3 default)
                changeStep(3);
            } else {
                alert("Por favor selecciona un producto.");
            }
        });

        // Deshabilitar botn Atrs en paso 1 (es el primer paso)
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
                
                // Verificar a qu paso ir: las prendas como RH, Gafetes, Presillas finalizan AQU (paso 3)
                const prendasTerminanPaso3 = ["rh", "gafete del nombre o apellido", "gafete", "presillas", "buso", "buso-manga-larga"];
                const productoActual = state.producto.toLowerCase();
                const isGorraEjercito = productoActual === "gorra" && state.identidad && state.identidad.toLowerCase() === "ejercito";

                if (prendasTerminanPaso3.includes(productoActual) || isGorraEjercito) {
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
            
            // Organize and format the summary data nicely
            let summaryText = "✅ ¡Personalización completada!\\n\\n";
            
            summaryText += "--- DATOS DEL CLIENTE ---\\n";
            summaryText += "• Nombre: " + (state.nombre || "No especificado") + "\\n";
            summaryText += "• Correo: " + (state.correo || "No especificado") + "\\n";
            summaryText += "• Teléfono: " + (state.telefono || "No especificado") + "\\n";
            summaryText += "• Dirección: " + (state.direccion || "No especificada") + "\\n";
            
            summaryText += "\\n--- INFORMACIÓN INSTITUCIONAL ---\\n";
            summaryText += "• Identidad/Fuerza: " + formatLabel(state.identidad) + "\\n";
            if (state.rango) {
                summaryText += "• Rango: " + state.rango + "\\n";
            }
            if (state.anoContingencia) {
                summaryText += "• Año de contingencia: " + state.anoContingencia + "\\n";
            }
            
            summaryText += "\\n--- DETALLES DEL PRODUCTO ---\\n";
            summaryText += "• Producto: " + (productLabels[state.producto] || formatLabel(state.producto)) + "\\n";
            if (state.color) {
                summaryText += "• Color: " + formatLabel(state.color) + "\\n";
            }
            if (state.talla) {
                summaryText += "• Talla: " + state.talla + "\\n";
            }
            if (state.tecnica) {
                summaryText += "• Técnica: " + (state.tecnica === "bordado" ? "Bordado" : "Impresión") + "\\n";
            }
            if (state.estampado) {
                summaryText += "• Estampado: " + formatLabel(state.estampado) + "\\n";
            }
            
            alert(summaryText);
        }

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
            if (validarPaso(4)) {
                const producto = productLabels[state.producto] || formatLabel(state.producto);
                const identidad = formatLabel(state.identidad);
                const tecnica = state.tecnica === "bordado" ? "Bordado" : "Impresión";
                const color = formatLabel(state.color);
                const estampado = state.estampado ? formatLabel(state.estampado) : "Ninguno";
                const talla = state.talla || "Sin talla";
                
                alert(`✅ Producto agregado al carrito:\n\nNombre: ${state.nombre}\nRango: ${state.rango}\nDirección: ${state.direccion}\nCorreo: ${state.correo}\nTeléfono: ${state.telefono}\nAño de contingencia: ${state.anoContingencia}\n\n${producto}\nIdentidad: ${identidad}\nTécnica: ${tecnica}\nColor: ${color}\nEstampado: ${estampado}\nTalla: ${talla}\nPrecio: ${priceMap[state.producto] || "$ 45.000"}`);
            } else {
                alert("⚠️ Por favor completa todos los campos antes de agregar al carrito");
            }
        });

        // Deshabilitar navegacin por pasos si no se han completado los requeridos
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
                // Hacer el contenedor del paso tambin no clickeable
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

        document.querySelectorAll("[data-estampado]").forEach((button) => {
            button.addEventListener("click", () => {
                if (window.getComputedStyle(button).display === "none") return;
                
                const tipoEstampado = button.dataset.estampado;
                
                // Si es distintivos, mostrar desplegable extra
                const dropdownContainer = document.getElementById("dropdown-distintivos-container");
                const dropdownEscudosContainer = document.getElementById("dropdown-escudos-container");
                if (tipoEstampado === "distintivos") {
                    if (dropdownContainer) dropdownContainer.style.display = "block";
                    if (dropdownEscudosContainer) dropdownEscudosContainer.style.display = "none";
                    // Guardar solo "distintivos" por ahora, se actualizarÃ¡ si elige una opciÃ³n del select
                    state.estampado = "distintivos";
                } else if (tipoEstampado === "escudos" && ['pañoleta', 'paÃ±oleta', 'panoleta', 'paoleta'].includes((state.producto || '').toLowerCase())) {
                    if (dropdownEscudosContainer) dropdownEscudosContainer.style.display = "block";
                    if (dropdownContainer) dropdownContainer.style.display = "none";
                    const selectEscudo = document.getElementById("select-escudo");
                    if (selectEscudo) {
                        const opt1 = Array.from(selectEscudo.options).find(o => o.value === "Estilo 1");
                        const optM1 = Array.from(selectEscudo.options).find(o => o.value === "Estilo -1");
                        const opt2 = Array.from(selectEscudo.options).find(o => o.value === "Estilo 2");
                        const optC2 = Array.from(selectEscudo.options).find(o => o.value === "Estilo ,2");
                        const opt3 = document.getElementById("opt-escudo-ejercito-3") || Array.from(selectEscudo.options).find(o => o.value === "Estilo 3");
                        const optC3 = document.getElementById("opt-escudo-ejercito-3b") || Array.from(selectEscudo.options).find(o => o.value === "Estilo ,3");
                        
                        if (state.identidad === "policia" || state.identidad === "armada") {
                            if (opt1) opt1.style.display = "";
                            if (optM1) optM1.style.display = "none";
                            if (opt2) opt2.style.display = "none";
                            if (optC2) optC2.style.display = "none";
                            if (opt3) opt3.style.display = "none";
                            if (optC3) optC3.style.display = "none";
                            
                            // Si es armada, ocultamos todo el contenedor dropdown para no dejar escoger estilo
                            // y asÃ­ obligar un solo diseÃ±o que mapeamos automÃ¡tico
                            if (state.identidad === "armada") {
                                if (dropdownEscudosContainer) dropdownEscudosContainer.style.display = "none";
                                state.estampado = "escudos";
                            } else {
                                selectEscudo.value = "Estilo 1";
                                state.estampado = "escudos - Estilo 1";
                            }
                        } else if (state.identidad === "gaula") {
                            if (opt1) opt1.style.display = "";
                            if (optM1) optM1.style.display = "none";
                            if (opt2) opt2.style.display = "";
                            if (optC2) optC2.style.display = "none";
                            if (opt3) opt3.style.display = "none";
                            if (optC3) optC3.style.display = "none";
                            selectEscudo.value = "Estilo 1";
                            state.estampado = "escudos - Estilo 1";
                        } else if (state.identidad === "ejercito") {
                            if (state.color === "negro") {
                                if (opt1) opt1.style.display = "";
                                if (optM1) optM1.style.display = "";
                                if (opt2) opt2.style.display = "none";
                                if (optC2) optC2.style.display = "none";
                                if (opt3) opt3.style.display = "none";
                                if (optC3) optC3.style.display = "none";
                                selectEscudo.value = "Estilo 1";
                                state.estampado = "escudos - Estilo 1";
                            } else if (state.color === "beiches") {
                                if (opt1) opt1.style.display = "none";
                                if (optM1) optM1.style.display = "none";
                                if (opt2) opt2.style.display = "";
                                if (optC2) optC2.style.display = "";
                                if (opt3) opt3.style.display = "none";
                                if (optC3) optC3.style.display = "none";
                                selectEscudo.value = "Estilo 2";
                                state.estampado = "escudos - Estilo 2";
                            } else if (state.color === "verde-claro") {
                                if (opt1) opt1.style.display = "none";
                                if (optM1) optM1.style.display = "none";
                                if (opt2) opt2.style.display = "none";
                                if (optC2) optC2.style.display = "none";
                                if (opt3) opt3.style.display = "";
                                if (optC3) optC3.style.display = "";
                                selectEscudo.value = "Estilo 3";
                                state.estampado = "escudos - Estilo 3";
                            } else {
                                if (opt1) opt1.style.display = "";
                                if (optM1) optM1.style.display = "";
                                if (opt2) opt2.style.display = "";
                                if (optC2) optC2.style.display = "";
                                if (opt3) opt3.style.display = "";
                                if (optC3) optC3.style.display = "";
                                selectEscudo.value = "";
                                state.estampado = "escudos";
                            }
                        } else {
                            if (opt1) opt1.style.display = "";
                            if (optM1) optM1.style.display = "none";
                            if (opt2) opt2.style.display = "";
                            if (optC2) optC2.style.display = "none";
                            if (opt3) opt3.style.display = "none";
                            if (optC3) optC3.style.display = "none";
                            selectEscudo.value = "";
                            state.estampado = "escudos";
                        }
                    } else {
                        state.estampado = "escudos";
                    }
                } else {
                    if (dropdownContainer) dropdownContainer.style.display = "none";
                    if (dropdownEscudosContainer) dropdownEscudosContainer.style.display = "none";
                    state.estampado = tipoEstampado;
                }

                setActiveClass(
                    document.querySelectorAll("[data-estampado]"),
                    (element) => element === button,
                    "seleccionada"
                );
                
                // Si cambia de estampado y tenia un distintivo, limpiar select
                const selectDistintivo = document.getElementById("select-distintivo");
                if (tipoEstampado !== 'distintivos' && selectDistintivo) {
                    selectDistintivo.value = "";
                }
                
                const selectEscudo = document.getElementById("select-escudo");
                if (tipoEstampado !== 'escudos' && selectEscudo) {
                    selectEscudo.value = "";
                }

                updateSummary();
            });
        });
        
        // Listener para el select de escudos
        const selectEscudo = document.getElementById("select-escudo");
        if (selectEscudo) {
            selectEscudo.addEventListener("change", (e) => {
                if (e.target.value) {
                    state.estampado = "escudos - " + e.target.value;
                } else {
                    state.estampado = "escudos";
                }
                updateSummary();
                validarPaso4Realtime();
            });
        }
        
        // Listener para el select de distintivos
        const selectDistintivo = document.getElementById("select-distintivo");
        if (selectDistintivo) {
            selectDistintivo.addEventListener("change", (e) => {
                if (e.target.value) {
                    state.estampado = "distintivos - " + e.target.value;
                } else {
                    state.estampado = "distintivos";
                }
                updateSummary();
                validarPaso4Realtime();
            });
        }
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
} catch(e) {
    alert('Error JS: ' + e.message + ' en linea ' + e.lineNumber);
    console.error(e);
}
})();














