import sys
import re

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

target_regex = r'// Letras mucho mas grandes[\s\S]*?(?=\s*\} else \{\s*overlayEl\.style\.display = "none";\s*\})'

replacement = """// Ajuste proporcional de tamaños para que sean equitativos y encajen
                divRango.style.fontWeight = "800";
                divRango.style.color = textColor;
                divRango.style.textShadow = shadowVal;
                
                divNombre.style.fontWeight = "900";
                divNombre.style.color = textColor;
                divNombre.style.textShadow = shadowVal;
                
                const rangoFinal = state.rango ? state.rango.charAt(0).toUpperCase() + state.rango.slice(1).toLowerCase() : 'Rango'; 
                const nombreFinal = state.nombre ? state.nombre.toUpperCase() : 'NOMBRE';
                divRango.textContent = rangoFinal;
                divNombre.textContent = nombreFinal;
                
                // Escalar el nombre para que quepa bien y sea similar en tamaño al rango
                let baseNombreSize = 16;
                let maxCharsNombre = 14;
                if (nombreFinal.length > maxCharsNombre) {
                    let newFontSize = (baseNombreSize * maxCharsNombre) / nombreFinal.length;
                    divNombre.style.fontSize = Math.max(9, newFontSize) + "px";
                } else {
                    divNombre.style.fontSize = baseNombreSize + "px";
                }
                
                // Escalar el rango para que sea equitativo y no se desborde
                let baseRangoSize = 12;
                let maxCharsRango = 18;
                if (rangoFinal.length > maxCharsRango) {
                    let newRangoSize = (baseRangoSize * maxCharsRango) / rangoFinal.length;
                    divRango.style.fontSize = Math.max(8, newRangoSize) + "px";
                } else {
                    divRango.style.fontSize = baseRangoSize + "px";
                }"""

new_text = re.sub(target_regex, replacement, text, count=1)

with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
    f.write(new_text)

print("Done with adjusting font sizes.")
