import sys
import re

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

target_regex = r'// Ajuste proporcional de tamaños para que sean equitativos y encajen[^}]*\} else \{[^}]*divRango\.style\.fontSize = baseRangoSize \+ "px";\s*\}'

replacement = """// Ajuste proporcional de tamaños para que sean equitativos y encajen y centrados
                divRango.style.fontWeight = "800";
                divRango.style.color = textColor;
                divRango.style.textShadow = shadowVal;
                divRango.style.textAlign = "center";
                divRango.style.width = "100%";
                
                divNombre.style.fontWeight = "900";
                divNombre.style.color = textColor;
                divNombre.style.textShadow = shadowVal;
                divNombre.style.textAlign = "center";
                divNombre.style.width = "100%";
                
                const rangoFinal = state.rango ? state.rango.charAt(0).toUpperCase() + state.rango.slice(1).toLowerCase() : 'Rango'; 
                const nombreFinal = state.nombre ? state.nombre.toUpperCase() : 'NOMBRE';
                divRango.textContent = rangoFinal;
                divNombre.textContent = nombreFinal;
                
                // Escalar el nombre para que quepa bien y sea similar en tamaño al rango
                let baseNombreSize = 11;
                let maxCharsNombre = 14;
                if (nombreFinal.length > maxCharsNombre) {
                    let newFontSize = (baseNombreSize * maxCharsNombre) / nombreFinal.length;
                    divNombre.style.fontSize = Math.max(6, newFontSize) + "px";
                } else {
                    divNombre.style.fontSize = baseNombreSize + "px";
                }
                
                // Escalar el rango para que sea equitativo y no se desborde
                let baseRangoSize = 7.5;
                let maxCharsRango = 18;
                if (rangoFinal.length > maxCharsRango) {
                    let newRangoSize = (baseRangoSize * maxCharsRango) / rangoFinal.length;
                    divRango.style.fontSize = Math.max(5, newRangoSize) + "px";
                } else {
                    divRango.style.fontSize = baseRangoSize + "px";
                }"""

new_text = re.sub(target_regex, replacement, text, count=1)

with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
    f.write(new_text)

print("Done")
