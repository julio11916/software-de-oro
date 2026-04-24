import re

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    c = f.read()

# Find updateSummary logic to update UI elements
# We need to hide the spans for contingencia, talla, estampado
def inject_ui_logic(match):
    return """
          const isEspecial = ["rh", "presillas", "gafete", "gafete del nombre o apellido", "pañoleta", "panoleta", "paoleta", "gorra", "pa\\u00f1oleta"].includes((state.producto || "").toLowerCase());

          // Hide UI items if especial
          const pContingencia = document.getElementById("preview-contingencia")?.parentElement;
          if (pContingencia) pContingencia.style.display = isEspecial ? "none" : "flex";
          const pTalla = document.getElementById("preview-talla")?.parentElement;
          if (pTalla) pTalla.style.display = isEspecial ? "none" : "flex";
          if (isEspecial && (state.producto || "").toLowerCase() !== "gorra") {
              const pEstampado = document.getElementById("preview-estampado")?.parentElement;
              if (pEstampado) pEstampado.style.display = "none";
          } else {
              const pEstampado = document.getElementById("preview-estampado")?.parentElement;
              if (pEstampado) pEstampado.style.display = "flex";
          }
""" + match.group(0)

c = re.sub(r'\s*let descripcionCompleta = \\$\{identidad\} \| \$\{tecnica\}\;', inject_ui_logic, c)

c = c.replace('["rh", "presillas", "gafete", "gafete del nombre o apellido", "paoleta", "panoleta", "paÃƒÂ±oleta"]', 
              '["rh", "presillas", "gafete", "gafete del nombre o apellido", "pañoleta", "panoleta", "paoleta", "gorra"]')

# We also need to fix the case where gorras have only "impresion delantera"
with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
    f.write(c)

print("done script")
