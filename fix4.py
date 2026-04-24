t = open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8').read()
start_idx = t.find('        // Escudos en pañoletas')
end_idx = t.find('        } else {\n            let iconClass = getProductIcon() || "fa-palette";')

if start_idx != -1 and end_idx != -1:
    print("Found! Rewriting...")
    new_txt = t[:start_idx] + """
        // Escudos en pañoletas
        const isPanoleta = ['pañoleta', 'panoleta', 'paoleta'].includes((state.producto || '').toLowerCase());
        if (isPanoleta && state.estampado && state.estampado.toLowerCase() === 'escudos') {
            const identId = state.identidad ? state.identidad.toLowerCase().trim() : 'policia';
            let escImgSrc = '';
            let c = (state.color || 'verde-claro').replace('-claro', '');
            if (identId === 'ejercito') escImgSrc = `/static/img/estampados/ejercito/pañoleta/Escudos/${c}.png`;
            else if (identId === 'gaula') escImgSrc = `/static/img/estampados/gaula/pañoleta/Escudos/escudo.png`;
            else escImgSrc = `/static/img/estampados/Policia/pañoleta/Escudos/escudo_${c}.png`;
            
            let muestraPanoleta = preview.querySelector("#estampado-panoleta");
            if (!muestraPanoleta) {
                muestraPanoleta = document.createElement("img");
                muestraPanoleta.id = "estampado-panoleta";
                muestraPanoleta.style.position = "absolute";
                muestraPanoleta.style.top = "50%";
                muestraPanoleta.style.left = "50%";
                muestraPanoleta.style.transform = "translate(-50%, -50%) scale(1)";
                muestraPanoleta.style.maxWidth = "60px";
                muestraPanoleta.style.maxHeight = "60px";
                muestraPanoleta.style.zIndex = "8";
                preview.querySelector("#preview-container").appendChild(muestraPanoleta);
            }
            muestraPanoleta.src = escImgSrc;
            muestraPanoleta.style.display = "block";
            let imgEl2 = preview.querySelector("#imagen-producto");
            if (imgEl2) imgEl2.style.mixBlendMode = "multiply";
        } else {
            let muestraPanoleta = preview.querySelector("#estampado-panoleta");
            if (muestraPanoleta) muestraPanoleta.style.display = "none";
        }
""" + t[end_idx:]
    with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
        f.write(new_txt)
    print("Done")
else:
    print("Not found!")