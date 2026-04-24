import re

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    c = f.read()

def inject_ui_logic(match):
    return match.group(0) + """
          // Hide UI items if especial
          const pCont = document.getElementById("preview-descripcion")?.parentElement?.parentElement?.children;
          if (pCont) {
              // we can iterate over info-items and hide by their labels if we want, or just hide by index.
              // Wait, the HTML has specific elements. Let's find preview-talla and preview-estampado
              let pTalla = document.getElementById("preview-talla")?.parentElement;
              if (pTalla) pTalla.style.display = isEspecial ? "none" : "flex";
              
              let pEstampado = document.getElementById("preview-estampado")?.parentElement;
              if (pEstampado) pEstampado.style.display = (isEspecial && (state.producto || "").toLowerCase() !== "gorra") ? "none" : "flex";
          }
"""

# Let's inject after let descripcionCompleta
c = re.sub(r'let descripcionCompleta = \$\{identidad\} \| \$\{tecnica\};', inject_ui_logic, c)

with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
    f.write(c)

print("done script3")
