t = open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8').read()
idx = t.find('if (isRh && state.vistaPrenda !== "trasera") {')
end = t.find('else if (isGafete && state.vistaPrenda !== "trasera") {', idx)

new_block = """if (isRh && state.vistaPrenda !== "trasera") {
                if (rhOverlayEl && state.modeloRh) {
                    // Para el ejercito ocultamos el texto porque las imágenes ya lo traen horneado
                    if (state.identidad === "ejercito") {
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
        """
t = t[:idx] + new_block + t[end:]
open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8').write(t)
print("rewrote isRh block")