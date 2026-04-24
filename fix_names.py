import sys

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

target = '                // Letras mucho mas grandes`r`n                  divRango.style.fontSize = "9px";`r`n                  divRango.style.fontWeight = "600";`r`n                  divRango.style.color = textColor;`r`n                  divRango.style.textShadow = shadowVal;`r`n`r`n                  divNombre.style.fontSize = "20px";`r`n                  divNombre.style.fontWeight = "900";`r`n                  divNombre.style.color = textColor;`r`n                  divNombre.style.textShadow = shadowVal;`r`n`r`n                  const rangoFinal = state.rango ? state.rango.charAt(0).toUpperCase() + state.rango.slice(1).toLowerCase() : \'Rango\'; const nombreFinal = state.nombre ? state.nombre.toUpperCase() : \'NOMBRE\'; divRango.textContent = rangoFinal;`r`n                  divNombre.textContent = nombreFinal;'

replacement = """
                // Letras mucho mas grandes
                divRango.style.fontSize = "9px";
                divRango.style.fontWeight = "600";
                divRango.style.color = textColor;
                divRango.style.textShadow = shadowVal;
                
                divNombre.style.fontWeight = "900";
                divNombre.style.color = textColor;
                divNombre.style.textShadow = shadowVal;
                
                const rangoFinal = state.rango ? state.rango.charAt(0).toUpperCase() + state.rango.slice(1).toLowerCase() : 'Rango'; 
                const nombreFinal = state.nombre ? state.nombre.toUpperCase() : 'NOMBRE';
                divRango.textContent = rangoFinal;
                divNombre.textContent = nombreFinal;
                
                // Dynamic font size for the name to fit the container
                // Assuming max length is around 12 characters for 20px
                let maxChars = 12;
                let baseFontSize = 26; // a bit bigger by default if possible
                if (nombreFinal.length > maxChars) {
                    let newFontSize = (baseFontSize * maxChars) / nombreFinal.length;
                    divNombre.style.fontSize = Math.max(9, newFontSize) + "px";
                } else {
                    divNombre.style.fontSize = baseFontSize + "px";
                }
                
                // Same for range to prevent overflow
                if (rangoFinal.length > 20) {
                    divRango.style.fontSize = "7.5px";
                }
"""

if target in text:
    print('Target exactly matched and replaced.')
    text = text.replace(target, replacement)
else:
    print('Target string not exact, trying regex or loose match.')
    import re
    # We can match everything starting from "// Letras mucho mas grandes" to "divNombre.textContent = nombreFinal;"
    pat = re.compile(r'\s*// Letras mucho mas grandes.*?divNombre\.textContent = nombreFinal;', re.DOTALL)
    if pat.search(text):
        print('Matched via regex and replaced.')
        text = pat.sub(replacement, text)

with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
    f.write(text)

print("Done")
