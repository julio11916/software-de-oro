import sys
with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

target = """            if (isRh && state.vistaPrenda !== "trasera") {
                if (rhOverlayEl && state.modeloRh) {
                    rhOverlayEl.style.display = "block";"""

replacement = """            if (isRh && state.vistaPrenda !== "trasera") {
                if (rhOverlayEl && state.modeloRh) {
                    // Para el ejercito ocultamos el texto porque las imágenes ya lo traen horneado
                    if (state.identidad === "ejercito") {
                        rhOverlayEl.style.display = "none";
                    } else {
                        rhOverlayEl.style.display = "block";
                    }"""

if target in text:
    print("Found! Replacing.")
    text = text.replace(target, replacement)
    with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
        f.write(text)
else:
    print("Target not found.")

