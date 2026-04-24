import re

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    c = f.read()

replace_text = """    if (llevaEstampado && (state.pasoActual >= 4)) {
        descripcionCompleta +=  | Estampado: ;
    }

    // Ocultar Talla, Contingencia y Estampado del panel derecho si no aplican
    let pTal = document.getElementById("preview-talla");
    if (pTal && pTal.parentElement) {
        pTal.parentElement.style.display = isEspecial ? "none" : "flex";
    }

    let pEst = document.getElementById("preview-estampado");
    if (pEst && pEst.parentElement) {
        pEst.parentElement.style.display = (isEspecial && (state.producto || "").toLowerCase() !== "gorra" && (state.producto || "").toLowerCase() !== "pa\\u00f1oleta" && (state.producto || "").toLowerCase() !== "panoleta") ? "none" : "flex";
    }
"""

c = re.sub(r'if \(llevaEstampado && \(state.pasoActual >= 4\)\) \{(?:\r?\n.*?){1,2}\}', replace_text, c)

with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
    f.write(c)

print("done finalize3")
