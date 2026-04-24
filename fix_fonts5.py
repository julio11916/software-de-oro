import sys

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

target = """// Ajuste proporcional de tamaños para que sean equitativos y encajen y centrados
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

replacement = """// Ajuste proporcional de tamaños para que sean equitativos y encajen y centrados
                divRango.style.fontWeight = "800";
                divRango.style.color = textColor;
                divRango.style.textShadow = shadowVal;
                divRango.style.textAlign = "center";
                divRango.style.width = "100%";
                divRango.style.margin = "0 0 1px 0"; // Mueve el rango un toque para separarlo
                divRango.style.padding = "0";
                
                divNombre.style.fontWeight = "900";
                divNombre.style.color = textColor;
                divNombre.style.textShadow = shadowVal;
                divNombre.style.textAlign = "center";
                divNombre.style.width = "100%";
                divNombre.style.margin = "0";
                divNombre.style.padding = "0";
                
                const rangoFinal = state.rango ? state.rango.charAt(0).toUpperCase() + state.rango.slice(1).toLowerCase() : 'Rango'; 
                const nombreFinal = state.nombre ? state.nombre.toUpperCase() : 'NOMBRE';
                divRango.textContent = rangoFinal;
                divNombre.textContent = nombreFinal;
                
                // Escalar el nombre para que quepa bien y sea centrar
                let baseNombreSize = 7.5;
                let maxCharsNombre = 14;
                if (nombreFinal.length > maxCharsNombre) {
                    let newFontSize = (baseNombreSize * maxCharsNombre) / nombreFinal.length;
                    divNombre.style.fontSize = Math.max(5, newFontSize) + "px";
                } else {
                    divNombre.style.fontSize = baseNombreSize + "px";
                }
                
                // Escalar el rango para que sea equitativo y mas pequeño y centrado
                let baseRangoSize = 5;
                let maxCharsRango = 18;
                if (rangoFinal.length > maxCharsRango) {
                    let newRangoSize = (baseRangoSize * maxCharsRango) / rangoFinal.length;
                    divRango.style.fontSize = Math.max(3.5, newRangoSize) + "px";
                } else {
                    divRango.style.fontSize = baseRangoSize + "px";
                }"""

if target in text:
    print("Found! Replacing.")
    text = text.replace(target, replacement)
    with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
        f.write(text)
else:
    print("Not found.")
