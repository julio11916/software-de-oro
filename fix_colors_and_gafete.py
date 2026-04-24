import re

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix colorMatriz for ejercito
ejercito_regex = r'("ejercito"\s*:\s*\{.*?\}),?\n\s*"policia"'
ejercito_match = re.search(ejercito_regex, text, re.DOTALL)
if ejercito_match:
    ej_block = ejercito_match.group(1)
    
    # Update gorra
    ej_block = re.sub(r'("gorra"\s*:\s*\[)["\w\-,\s]+(\])', r'\1"verde-claro", "negro", "beiches"\2', ej_block)
    
    # Update panoleta variants
    ej_block = re.sub(r'("paoleta"\s*:\s*\[)["\w\-,\s]+(\])', r'\1"verde-claro", "negro", "beiches"\2', ej_block)
    ej_block = re.sub(r'("panoleta"\s*:\s*\[)["\w\-,\s]+(\])', r'\1"verde-claro", "negro", "beiches"\2', ej_block)
    ej_block = re.sub(r'("pañoleta"\s*:\s*\[)["\w\-,\s]+(\])', r'\1"verde-claro", "negro", "beiches"\2', ej_block)
    
    text = text.replace(ejercito_match.group(1), ej_block)
    print("Updated colorMatriz for ejercito")

# Fix Gafete nombre logic
gafete_target = """                const rangoFinal = state.rango ? state.rango.charAt(0).toUpperCase() + state.rango.slice(1).toLowerCase() : 'Rango'; 
                const nombreFinal = state.nombre ? state.nombre.toUpperCase() : 'NOMBRE';
                divRango.textContent = rangoFinal;
                divNombre.textContent = nombreFinal;"""

gafete_replacement = """                const rangoFinal = state.rango ? state.rango.charAt(0).toUpperCase() + state.rango.slice(1).toLowerCase() : 'Rango'; 
                let nombreFinalRaw = state.nombre ? state.nombre.toUpperCase().trim() : 'NOMBRE';
                
                // Lógica de Ejército: Solo Apellido
                const identId = state.identidad ? state.identidad.toLowerCase().trim() : '';
                if (identId === 'ejercito' && nombreFinalRaw !== 'NOMBRE') {
                    let partes = nombreFinalRaw.split(/\s+/);
                    if (partes.length === 2) {
                        nombreFinalRaw = partes[1]; 
                    } else if (partes.length === 3) {
                        nombreFinalRaw = partes[2]; 
                    } else if (partes.length >= 4) {
                        nombreFinalRaw = partes[2]; // Primer apellido usualmente en 4 palabras
                    }
                }
                
                const nombreFinal = nombreFinalRaw;

                divRango.textContent = rangoFinal;
                divNombre.textContent = nombreFinal;"""

if gafete_target in text:
    text = text.replace(gafete_target, gafete_replacement)
    print("Updated Gafete logic")

with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
    f.write(text)
