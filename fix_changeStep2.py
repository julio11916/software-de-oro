import re

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

target_regex = r'(\s*state\.pasoActual = step;\s*// \?\? Actualizar Layout PRIMERO)'
replacement = r"""
        // Al retroceder, limpiar los estados de los pasos futuros para que vuelva al estado en que estaba
        if (step < state.pasoActual) {
            if (step === 3) {
                // De 4 a 3: limpiamos el estampado
                state.estampado = null;
                const dropdownDist = document.getElementById("dropdown-distintivos-container");
                if (dropdownDist) dropdownDist.style.display = "none";
                const selectDist = document.getElementById("select-distintivo");
                if (selectDist) selectDist.value = "";
                document.querySelectorAll("[data-estampado]").forEach(btn => btn.classList.remove("seleccionada"));
            } else if (step === 2) {
                // De 3 a 2: limpiamos color, rh, talla, vista
                state.color = null;
                state.estampado = null;
                state.modeloRh = null;
                document.querySelectorAll("[data-color]").forEach(btn => btn.classList.remove("seleccionada"));
            } else if (step === 1) {
                // De 2 a 1: limpiamos producto y lo que sigue
                state.producto = null;
                state.color = null;
                state.estampado = null;
                state.modeloRh = null;
                document.querySelectorAll("[data-producto]").forEach(btn => btn.classList.remove("seleccionada"));
            }
        }\1"""

new_text = re.sub(target_regex, replacement, text)

if text != new_text:
    print("Replaced!")
    with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
        f.write(new_text)
else:
    print("Not replaced!")
