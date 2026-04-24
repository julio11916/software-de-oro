# -*- coding: utf-8 -*-
import re
path = 'static/js/usuario/orden_personalizada.js'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

new_block = '''                if (tipoEstampado === "distintivos") {
                    if (dropdownContainer) dropdownContainer.style.display = "block";
                    if (dropdownEscudosContainer) dropdownEscudosContainer.style.display = "none";
                    state.estampado = "distintivos";
                } else if (tipoEstampado === "escudos" && ['pañoleta', 'panoleta', 'paoleta'].includes((state.producto || '').toLowerCase())) {
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
                } else {'''

text = text.replace(re.search(r'if \(tipoEstampado === "distintivos"\) \{.*?\} else \{', text, flags=re.DOTALL).group(0), new_block)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
