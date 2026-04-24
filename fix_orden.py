import re

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update Gafete Image

old_gafete_img = '''// GAFETE
        if (productName.includes("gafete")) {
            if (identidad.includes("ejercito")) {
                return isBack
                    ? "/static/img/prendas/ejercito/gafete del nombre o apellido/reves-gafete.png"
                    : "/static/img/prendas/ejercito/gafete del nombre o apellido/frente.png";
            } else if (identidad.includes("gaula")) {'''

new_gafete_img = '''// GAFETE
        if (productName.includes("gafete")) {
            if (identidad.includes("ejercito")) {
                return isBack
                    ? "/static/img/prendas/ejercito/gafete del nombre o apellido/reves-gafete.png"
                    : "/static/img/prendas/ejercito/gafete del nombre o apellido/frente.png";
            } else if (identidad.includes("gaula")) {'''

# This seems already correct, let's verify if `frente.png` is being returned. 
# Yes, it's matching. But user said "aplica la imagen de frente en el gafete y solo el nombre no implementes el rango es este gafete del ejercito"
# Okay, so I don't need to change `getProductImage` because it ALREADY uses `frente.png`. I just need to hide the rank and maybe center the name.

# 2. Hide Rango for Ejercito Gafete

old_overlay = '''                const nombreFinal = nombreFinalRaw;

                divRango.textContent = rangoFinal;
                divNombre.textContent = nombreFinal;

                // Escalar el nombre para que quepa bien y sea centrar
                let baseNombreSize = 7.5;'''

new_overlay = '''                const nombreFinal = nombreFinalRaw;

                if (identId === 'ejercito') {
                    divRango.style.display = 'none';
                    // Optional: si es necesario centrar más
                } else {
                    divRango.style.display = 'block';
                    divRango.textContent = rangoFinal;
                }
                
                divNombre.textContent = nombreFinal;

                // Escalar el nombre para que quepa bien y sea centrar
                let baseNombreSize = 7.5;'''

text = text.replace(old_overlay, new_overlay)

# 3. Update finalizarOrden Alert Message
# Let's extract that function.
import ast
old_finalizar = ""
idx = text.find('function finalizarOrden() {')
if idx != -1:
    end_idx = text.find('}', idx)
    # let's just use string replace on the alert string.
pass

with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
    f.write(text)
    
print("Updated overlay")
