import re

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

bad_block_pattern = r'if \(llevaEstampado && \(state\.pasoActual >= 4\)\) \{\s*descripcionCompleta \+= \ \| Estampado: \$\{estampado\}\s*// Ocultar Talla.*?flex\";\s*\}\s*\;\s*\}'

correct_block = """if (llevaEstampado && (state.pasoActual >= 4)) {
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
}"""

# Actually, let's just find the start of if (llevaEstampado and the end of } after ;
# Since it's easier to find indexes:
start_idx = text.find('if (llevaEstampado && (state.pasoActual >= 4)) {')
end_idx = text.find('// Actualizar panel derecho', start_idx)

if start_idx != -1 and end_idx != -1:
    text = text[:start_idx] + correct_block + '\n\n        ' + text[end_idx:]
else:
    print("Could not find bounds")

with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
    f.write(text)

print("done syntax")
