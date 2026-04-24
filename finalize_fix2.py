import re

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    c = f.read()

find_text = "descripcionCompleta +=  | Estampado: ;\n          }"
replace_text = find_text + """
          // Ocultar Talla, Contingencia y Estampado del panel derecho si no aplican
          let pContingencia = document.getElementById("preview-descripcion")?.parentElement?.parentElement?.children;
          if (pContingencia) {
             let pTal = document.getElementById("preview-talla")?.parentElement;
             if (pTal) pTal.style.display = isEspecial ? "none" : "flex";
             let pEst = document.getElementById("preview-estampado")?.parentElement;
             if (pEst) pEst.style.display = (isEspecial && (state.producto || "").toLowerCase() !== "gorra" && (state.producto || "").toLowerCase() !== "pa\\u00f1oleta" && (state.producto || "").toLowerCase() !== "panoleta") ? "none" : "flex";
          }
"""

c = c.replace(find_text, replace_text)

with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
    f.write(c)

print("done finalize2")
