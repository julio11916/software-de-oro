import re
path = "static/js/usuario/orden_personalizada.js"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

old_block = r"""                if (tipoEstampado === "distintivos") {
                    if (dropdownContainer) dropdownContainer.style.display = "block";
                    if (dropdownEscudosContainer) dropdownEscudosContainer.style.display = "none";
                    // Guardar solo "distintivos" por ahora, se actualizará si elige una opción del select
                    state.estampado = "distintivos";
                } else if (tipoEstampado === "escudos" && ['pañoleta', 'panoleta', 'paoleta'].includes((state.producto || '').toLowerCase())) {
                    if (dropdownEscudosContainer) dropdownEscudosContainer.style.display = "block";
                    if (dropdownContainer) dropdownContainer.style.display = "none";
                    state.estampado = "escudos";
                } else {"""

# The regex should match regardless of encoding glitches
new_block = """                if (tipoEstampado === "distintivos") {
                    if (dropdownContainer) dropdownContainer.style.display = "block";
                    if (dropdownEscudosContainer) dropdownEscudosContainer.style.display = "none";
                    state.estampado = "distintivos";
                } else if (tipoEstampado === "escudos" && ['pañoleta', 'pa\\u00f1oleta', 'panoleta', 'paoleta'].includes((state.producto || '').toLowerCase())) {
                    if (dropdownEscudosContainer) dropdownEscudosContainer.style.display = "block";
                    if (dropdownContainer) dropdownContainer.style.display = "none";
                    
                    const selectEsc = document.getElementById("select-escudo");
                    if (selectEsc) {
                        const opt2 = Array.from(selectEsc.options).find(o => o.value === "Estilo 2");
                        if (state.identidad === "policia") {
                            if (opt2) opt2.style.display = "none";
                            selectEsc.value = "Estilo 1";
                            state.estampado = "escudos - Estilo 1";
                        } else {
                            if (opt2) opt2.style.display = "";
                            state.estampado = "escudos";
                        }
                    } else {
                        state.estampado = "escudos";
                    }
                } else {"""

text = re.sub(r'if \(tipoEstampado === "distintivos"\) \{.*?\} else \{', new_block, text, flags=re.DOTALL)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)
