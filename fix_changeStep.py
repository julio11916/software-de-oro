import sys
with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

target = """        state.pasoActual = step;

        // ?? Actualizar Layout PRIMERO (para evitar que cualquier error detenga esto)"""

replacement = """        // Al retroceder, limpiar los estados de los pasos futuros
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
                // De 3 a 2: limpiamos color y rh
                state.color = null;
                state.modeloRh = null;
                state.estampado = null;
                document.querySelectorAll("[data-color]").forEach(btn => btn.classList.remove("seleccionada"));
            } else if (step === 1) {
                // De 2 a 1: limpiamos producto
                state.producto = null;
                state.color = null;
                state.modeloRh = null;
                state.estampado = null;
                document.querySelectorAll("[data-producto]").forEach(btn => btn.classList.remove("seleccionada"));
            }
        }

        state.pasoActual = step;

        // ?? Actualizar Layout PRIMERO (para evitar que cualquier error detenga esto)"""

if target in text:
    print("Found target!")
    text = text.replace(target, replacement)
    with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
        f.write(text)
else:
    print("Target NOT found!")
