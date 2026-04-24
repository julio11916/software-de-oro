import re

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update gorra color for ejercito
ej_match = re.search(r'("ejercito"\s*:\s*\{)(.*?)(\}\s*,\s*"policia")', text, re.DOTALL)
if ej_match:
    ej_block = ej_match.group(2)
    # Set gorra to "verde-claro"
    ej_block = re.sub(r'("gorra"\s*:\s*\[)[^\]]*(\])', r'\1"verde-claro"\2', ej_block)
    text = text[:ej_match.start(2)] + ej_block + text[ej_match.end(2):]

# 2. Update logic for 'Siguiente' or 'Finalizar' in Step 3/4
# We need to find `changeStep` and `bindNavigation`.
target_changeStep = """            if (btnPasos3) {
                const prendasTerminanPaso3 = ["rh", "gafete del nombre o apellido", "gafete", "presillas", "buso", "buso-manga-larga"];
                if (prendasTerminanPaso3.includes(productoActual)) {"""

# Replace it with check for ejercito & gorra
replacement_changeStep = """            if (btnPasos3) {
                const prendasTerminanPaso3 = ["rh", "gafete del nombre o apellido", "gafete", "presillas", "buso", "buso-manga-larga"];
                const isGorraEjercito = productoActual === "gorra" && state.identidad && state.identidad.toLowerCase() === "ejercito";
                if (prendasTerminanPaso3.includes(productoActual) || isGorraEjercito) {"""

text = text.replace(target_changeStep, replacement_changeStep)

target_bindNavigation = """                const prendasTerminanPaso3 = ["rh", "gafete del nombre o apellido", "gafete", "presillas", "buso", "buso-manga-larga"];
                const productoActual = state.producto.toLowerCase();

                if (prendasTerminanPaso3.includes(productoActual)) {"""

replacement_bindNavigation = """                const prendasTerminanPaso3 = ["rh", "gafete del nombre o apellido", "gafete", "presillas", "buso", "buso-manga-larga"];
                const productoActual = state.producto.toLowerCase();
                const isGorraEjercito = productoActual === "gorra" && state.identidad && state.identidad.toLowerCase() === "ejercito";

                if (prendasTerminanPaso3.includes(productoActual) || isGorraEjercito) {"""

text = text.replace(target_bindNavigation, replacement_bindNavigation)

# Check Image
# Let's ensure the getProductColorImage correctly returns the image for gorra verde-claro.
# `if (identidad === "ejercito") return \`/static/img/prendas/ejercito/gorras/gorra_${colorName === 'negro' ? 'negra' : colorName}.png\`;`
# Since we only have "verde-claro", it should be "/static/img/prendas/ejercito/gorras/gorra_verde.png".

with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated gorra logic for ejercito.")
