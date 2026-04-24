import re

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    c = f.read()

# Make sure we add DOM hiding logic right at the end of updateSummary
def inject_at_end_of_summary(match):
    return match.group(0) + """
          // Ocultar Talla, Contingencia y Estampado del panel derecho si no aplican
          let pContingencia = document.getElementById("preview-descripcion")?.parentElement?.parentElement?.children;
          if (pContingencia) {
             let pTal = document.getElementById("preview-talla")?.parentElement;
             if (pTal) pTal.style.display = isEspecial ? "none" : "flex";
             let pEst = document.getElementById("preview-estampado")?.parentElement;
             if (pEst) pEst.style.display = (isEspecial && (state.producto || "").toLowerCase() !== "gorra" && (state.producto || "").toLowerCase() !== "pa\\u00f1oleta" && (state.producto || "").toLowerCase() !== "panoleta") ? "none" : "flex";
          }
"""

c = re.sub(r'(descripcionCompleta \+= \ \| Estampado: \$\{estampado\}\;\s*\n\s*\})', inject_at_end_of_summary, c)

with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
    f.write(c)

print("done finalize")
